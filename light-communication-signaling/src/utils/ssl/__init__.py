from twisted.python.modules import getModule

def get_public_cert():
    return getModule(__name__).filePath.sibling('public.pem').getContent()

def get_server_cert():
    return getModule(__name__).filePath.sibling('server.pem').getContent()
