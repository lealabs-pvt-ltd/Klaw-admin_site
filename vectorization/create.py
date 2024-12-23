import chromadb



def access_collection(dbname):
    # Create a persistent ChromaDB client
    client = chromadb.PersistentClient(path="db/")

    """

    persist_directory="db/": This tells ChromaDB where to save its data on your computer. 
    The "db/" means it will create a folder named "db" in your current working directory to store all the information.


    """



    # Create a collection for storing your PDF data
    collection = client.get_or_create_collection(name=dbname)  # collection is a cabinet for holding all of your files.

    print("db accessed successfully")

    return collection
