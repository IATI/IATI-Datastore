import iatilib

if __name__ == '__main__':
    import sys
    try:
        iatilib.importer.load_package()
    except Exception, e:
        print 'Failed:', e
        logtext = "Couldn't load package: " + str(e) + "\n"
        log(logtext)
    print iatilib.Session.query(iatilib.model.Activity).count()
    print iatilib.Session.query(iatilib.model.Transaction).count()
