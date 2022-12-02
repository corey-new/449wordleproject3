games: hypercorn games --reload --debug --bind games.local.gd:$PORT --access-logfile - --error-logfile - --log-level DEBUG
games: hypercorn games --reload --debug --bind games.local.gd:$PORT --access-logfile - --error-logfile - --log-level DEBUG
games: hypercorn games --reload --debug --bind games.local.gd:$PORT --access-logfile - --error-logfile - --log-level DEBUG

users: hypercorn users --reload --debug --bind users.local.gd:$PORT --access-logfile - --error-logfile - --log-level DEBUG

primary: ./bin/litefs -config ./etc/primary.yml
secondary1: ./bin/litefs -config ./etc/secondary1.yml
secondary2: ./bin/litefs -config ./etc/secondary2.yml
