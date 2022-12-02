users: hypercorn users --reload --debug --bind users.local.gd:$PORT --access-logfile - --error-logfile - --log-level DEBUG
primary: ./bin/litefs -config ./etc/primary.yml
games1: hypercorn games --reload --debug --bind games.local.gd:$PORT --access-logfile - --error-logfile - --log-level DEBUG
secondary1: ./bin/litefs -config ./etc/secondary1.yml
games2: hypercorn games --reload --debug --bind games.local.gd:$PORT --access-logfile - --error-logfile - --log-level DEBUG
secondary2: ./bin/litefs -config ./etc/secondary2.yml
games3: hypercorn games --reload --debug --bind games.local.gd:$PORT --access-logfile - --error-logfile - --log-level DEBUG
