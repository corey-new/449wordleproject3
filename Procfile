users: hypercorn users --reload --debug --bind users.local.gd:$PORT --access-logfile - --error-logfile - --log-level DEBUG
games1: hypercorn games --reload --debug --bind games.local.gd:$PORT --access-logfile - --error-logfile - --log-level DEBUG
games2: hypercorn games --reload --debug --bind games.local.gd:$PORT --access-logfile - --error-logfile - --log-level DEBUG
games3: hypercorn games --reload --debug --bind games.local.gd:$PORT --access-logfile - --error-logfile - --log-level DEBUG

primary: ./bin/litefs -config ./etc/primary.yml
secondary: ./bin/litefs -config ./etc/secondary.yml
tertiary: ./bin/litefs -config ./etc/tertiary.yml
