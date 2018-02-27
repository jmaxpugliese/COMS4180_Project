#!/usr/bin/python
# -*- coding: utf-8 -*-

# start IDS class in 'listen' mode
    ## wait for connection

    ## read byte by byte and identifier signature

        ## if sig, drop message & log envent

        ## else, pass message to server

# obtain message
    ## process cmd through IDS

        ### `ls`
            #### return all file names

        ### `get`
            #### load file and send

        ### `put`
            #### save file

        ### send ACK


if __name__ == '__main__':
    sys.exit(main())
