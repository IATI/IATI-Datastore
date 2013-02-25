API Endpoints
=============

    access/
        /activity
        /activity/<id>
        /transaction
        /transaction/<id>                   # Have to invent an ID here
        /organisation/
        /organisation/<reporting-org-ref>   # {reporting-org/@ref}
        /participating-org                 # eg. ?role=Funding
        /participating-org/<id>
        /sector/<vocab>
        /sector/<vocab>/<code>              # what is this?
        /recipient-country                # I just made this up because I can
        /recipient-region                  # I just made this up because I can
        /recipient-country/<code> 
        /recipient-region/<code> 

    aggregate/
        /activity/                        # Count activities
        /transaction                       # Count transactions
        /organisation                      # Count organisations

    provenance/                             # TODO later

    about/                                  # TODO later
