import psycopg2
from psycopg2.sql import SQL, DEFAULT

from estnltk import logger

from estnltk.text import Text
from estnltk.converters import text_to_json

from estnltk.storage.postgres.pg_operations import collection_table_identifier
from estnltk.storage.postgres.buffered_table_insert import BufferedTableInsert


# TODO: this is a duplicate, but we can't import PgCollectionException 
#       from estnltk.storage.postgres. 
#       the issue with tangled imports needs to be solved
class PgCollectionException(Exception):
    pass


class CollectionTextObjectInserter(object):
    """Context manager for buffered insertion of Text objects into the collection.
       Optionally, metadata and keys of insertable Text objects can be specified 
       during the insertion. 
        
       Notes about layers. 
       1) Attached layers. After the first Text object has been inserted, its layers 
       will be taken as the attached layers of the collection. Which means that other 
       insertable Text objects must have exactly the same layers.
       (and attached layers cannot be changed after the first insertion)
       2) Detached layers. If this collection already has detached layer(s), new Text 
       objects cannot be inserted.
        
       Example usage 1. Insert Text objects with metadata, but wo annotation layers:
            # Create collection w metadata
            collection.create( meta=OrderedDict( [('my_meta', 'str')]) )
            # Insert into the collection
            with CollectionTextObjectInserter( collection ) as col_inserter:
                col_inserter.insert( Text( ... ), key=0, meta_data={'my_meta':'A'} )
                col_inserter.insert( Text( ... ), key=1, meta_data={'my_meta':'B'} )
                ...
                
       Example usage 2. Insert annotated Text objects:
            # Create collection
            collection.create()
            # Insert into the collection
            with CollectionTextObjectInserter( collection ) as col_inserter:
                col_inserter.insert( Text( ... ).tag_layer('words') )
                col_inserter.insert( Text( ... ).tag_layer('words') )
                ...
    """

    def __init__(self, collection, buffer_size=10000, query_length_limit=5000000):
        """Initializes context manager for Text object insertions.
        
        Parameters:
         
        :param collection: PgCollection
            Collection where Text objects will be inserted.
        :param buffer_size: int
            Maximum buffer size (in table rows) for the insert query. 
            If the size is met or exceeded, the insert buffer will be flushed. 
            (Default: 10000)
        :param query_length_limit: int
            Soft approximate insert query length limit in unicode characters. 
            If the limit is met or exceeded, the insert buffer will be flushed.
            (Default: 5000000)
        """
        if collection is None: # or (isinstance(collection, PgCollection) and not collection.exists()):
            raise PgCollectionException("collection does not exist, can't create inserter")
        #elif not isinstance(collection, PgCollection):
        #    raise TypeError('collection must be an instance of PgCollection')
        #
        # TODO: can't import PgCollection from estnltk.storage.postgres
        #       resolve the issue with tangled imports
        #
        self.collection = collection
        self.table_identifier = collection_table_identifier( self.collection.storage, self.collection.name )
        self.buffer_size = buffer_size
        self.query_length_limit = query_length_limit
        self.buffered_inserter = None
        self.insert_counter = 0


    def __enter__(self):
        """ Initializes the insertion buffer and does initial check-ups of the structure. """
        self.collection.storage.conn.commit()
        self.collection.storage.conn.autocommit = False
        # Make new buffered inserter
        self.buffered_inserter = BufferedTableInsert( self.collection.storage.conn, 
                                                      self.table_identifier,
                                                      columns = self.collection.column_names, 
                                                      query_length_limit = self.query_length_limit,
                                                      buffer_size = self.buffer_size )
        cursor = self.buffered_inserter.cursor
        assert cursor is not None
        # Check for existing detached layers
        if any(struct['layer_type'] == 'detached' for struct in self.collection.structure.structure.values()):
            raise PgCollectionException("this collection has detached layers, can't add new text objects")
        # Validate emptiness of the collection
        if self.collection._is_empty and len(self.collection) == 0:
            # Lock the table
            cursor.execute(SQL('LOCK TABLE {}').format(self.table_identifier))
            # Note: "There is no UNLOCK TABLE command; locks are always 
            # released at transaction end."
            # see more: https://www.postgresql.org/docs/9.4/sql-lock.html
            # TODO: the old implementation only locked the table iff it
            #       was empty. But shouldn't we always lock it?
            #
            # There should be no structure if the collection is empty
            # ( CollectionStructureBase should return None )
            if self.collection.structure is None:
                raise PgCollectionException("collection already has structure {}, can't create another".format( self.collection.structure.structure ))
        return self


    def __exit__(self, type, value, traceback):
        """ Closes the insertion buffer. """
        if self.buffered_inserter is not None:
            self.buffered_inserter.close()
            logger.info('inserted {} texts into the collection {!r}'.format(self.insert_counter, self.collection.name))


    def insert(self, text, key=None, meta_data=None):
        """Inserts given Text object into the collection.
           Optionally, metadata and key of insertable Text 
           object can be specified. 
        """
        assert isinstance(text, Text)
        assert self.buffered_inserter is not None
        # 1) Empty collection
        if self.collection._is_empty:
            self.collection._is_empty = False
            if len(self.collection) == 0:
                # Insert the first row
                if key is None:
                    key = 0
                row = [ key, text_to_json(text) ]
                for k in self.collection.column_names[2:]:
                    if k in meta_data:
                        m = meta_data[k]
                    else:
                        m = DEFAULT
                    row.append(m)
                self.buffered_inserter.insert( row )
                self.insert_counter += 1
                # set attached layers of the collection
                for layer in text.layers:
                    # TODO: meta = ???
                    self.collection.structure.insert(layer=text[layer], layer_type='attached', meta={})
                return
            self.collection.storage.conn.commit()
            self.collection.structure.load()
        # 2) Non-empty collection
        # Validate that insertable Text object has appropriate structure
        assert set(text.layers) == set(self.collection.structure), '{} != {}'.format(set(text.layers),
                                                                                     set(self.collection.structure))
        for layer_name in text.layers:
            layer = text[layer_name]
            layer_struct = self.collection.structure[layer_name]
            assert layer_struct['layer_type'] == 'attached'
            assert layer_struct['attributes'] == layer.attributes, '{} != {}'.format(
                    layer_struct['attributes'], layer.attributes)
            assert layer_struct['ambiguous'] == layer.ambiguous
            assert layer_struct['parent'] == layer.parent
            assert layer_struct['enveloping'] == layer.enveloping
            assert layer_struct['serialisation_module'] == layer.serialisation_module
        # Insert the next row
        if key is None:
            key = DEFAULT
        row = [key, text_to_json(text)]
        for k in self.collection.column_names[2:]:
            if k in meta_data:
                m = meta_data[k]
            else:
                m = DEFAULT
            row.append(m)
        self.buffered_inserter.insert( row )
        self.insert_counter += 1


