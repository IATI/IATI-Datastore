
API Endpoints
=============

    access/
        /activities
        /activity/<id>
        /transactions
        /transaction/<id>                   # Have to invent an ID here
        /organisations/
        /organisation/<reporting-org-ref>   # {reporting-org/@ref}
        /participating-orgs                 # eg. ?role=Funding
        /participating-org/<id>
        /sectors/<vocab>
        /sector/<vocab>/<code>              # what is this?
        /recipient-countries                # I just made this up because I can
        /recipient-regions                  # I just made this up because I can
        /recipient-country/<code> 
        /recipient-region/<code> 

    aggregate/
        /activities/                        # Count activities
        /transactions                       # Count transactions
        /organisations                      # Count organisations

    provenance/                             # TODO later

    about/                                  # TODO later
