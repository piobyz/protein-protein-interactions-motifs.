import sys, os
sys.path.append(os.path.abspath('.'))

def test_import():
    import workflow
    import DB_DIP
    import DB_3DID
    import misc
    print sys.path
