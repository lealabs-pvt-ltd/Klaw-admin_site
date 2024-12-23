



def create_chunks(text, chunk_size=100):
    # Split the text into chunks of a specified size
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]