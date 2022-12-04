# 449wordleproject2

### Initialization Stage 

- To configure nginx, copy the contents of the file `nginx-config` at the root of the project, into the file on your VM located at the path `/etc/nginx/sites-enabled/tutorial`

- Then, change directory into the project and run `sh bin/init.sh` to initialize the databases and populate the games database with valid words.

- Finally, start the services with the command `foreman start --formation users=1,games=3`

### Using the API

> Every endpoint requires BASIC authentication _except_ for `/auth/register`

- **Create an account** by making a `POST` request to the endpoint `/auth/register` like so:

  `http POST tuffix-vm/auth/register username=your_username password=your_password`

- **Start a game** by making a `POST` request to the endpoint `/games/create` like so:

  `http POST tuffix-vm/games/create -a your_username:your_password`

- **Make a guess** by making a `POST` request with a `guess` field to the endpoint `/games/<string:game_id>` like so:

  `http POST tuffix-vm/games/0accd498-44ed-4b48-b529-9fb52fae5666 -a your_username:your_password guess=YOUR_GUESS`

  > Note: you may only make guesses for games which you started.

- **Check game history** by making a `GET` request to the endpoint `/games/<string:game_id>` like so:

  `http tuffix-vm/games/0accd498-44ed-4b48-b529-9fb52fae5666 -a your_username:your_password`

  > Note: you may only access data for games which you started.

- **Retrieve in progress games** by making a `GET` request to the endpoint `/users/<string:username>` like so:

  `http tuffix-vm/users/your_username -a your_username:your_password`

  > Note: you cannot access another users' games.
