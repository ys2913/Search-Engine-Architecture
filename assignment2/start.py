import tornado.ioloop
import inventory as inv
import frontend as front
import indexer as indexer
import doc_servers as docs
import index_servers as inds



if __name__ == "__main__":
    # For Set flag for Indexer to True in inventory.py
    if inv.RUN_INDEXER:
        print("Indexer Running")
        indexer.init_indexer()
        print("Indexer Completed")
    else:
        print("Indexer Not Ruuning")
        print("Set RUN_INDEXER = True in inventory.py for running the indexer")

    # starting frontend
    front.init_frontend()
    # starting index servers
    inds.init_index_servers()
    # starting document servers
    docs.init_doc_servers()
    tornado.ioloop.IOLoop.current().start()