PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;

DROP TABLE IF EXISTS valid_words;
DROP TABLE IF EXISTS game_history;
DROP TABLE IF EXISTS game_states;
DROP TABLE IF EXISTS games;

CREATE TABLE games (
    game_id TEXT NOT NULL,
    secret_word TEXT NOT NULL,
    username TEXT NOT NULL,
    PRIMARY KEY(game_id)
);

CREATE TABLE game_states (
    game_id TEXT NOT NULL,
    remaining_guesses TINYINT NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (game_id) REFERENCES games(game_id)
);

CREATE TABLE game_history (
    game_id TEXT NOT NULL,
    guess TEXT NOT NULL,
    remaining_guesses TINYINT NOT NULL,
    FOREIGN KEY (game_id) REFERENCES games(game_id)
);

CREATE TABLE valid_words (
    word TEXT NOT NULL,
    correct_word BOOLEAN NOT NULL,
    PRIMARY KEY(word)
);

INSERT INTO games VALUES ("0e095c23-d5af-4907-b7ab-e0a369d8f5fc", "cigar", "john");
INSERT INTO game_states VALUES ("0e095c23-d5af-4907-b7ab-e0a369d8f5fc", 2, "In Progress");
INSERT INTO game_history VALUES ("0e095c23-d5af-4907-b7ab-e0a369d8f5fc", "cited", 5);
INSERT INTO game_history VALUES ("0e095c23-d5af-4907-b7ab-e0a369d8f5fc", "amice", 4);
INSERT INTO game_history VALUES ("0e095c23-d5af-4907-b7ab-e0a369d8f5fc", "baccy", 3);
INSERT INTO game_history VALUES ("0e095c23-d5af-4907-b7ab-e0a369d8f5fc", "aglet", 2);
INSERT INTO games VALUES ("02fb4749-3556-4196-9b63-aa08baff4fef", "rebut", "john");
INSERT INTO game_states VALUES ("02fb4749-3556-4196-9b63-aa08baff4fef", 0, "lost");
INSERT INTO game_history VALUES ("02fb4749-3556-4196-9b63-aa08baff4fef", "aahed", 5);
INSERT INTO game_history VALUES ("02fb4749-3556-4196-9b63-aa08baff4fef", "aalii", 4);
INSERT INTO game_history VALUES ("02fb4749-3556-4196-9b63-aa08baff4fef", "aapas", 3);
INSERT INTO game_history VALUES ("02fb4749-3556-4196-9b63-aa08baff4fef", "aargh", 2);
INSERT INTO game_history VALUES ("02fb4749-3556-4196-9b63-aa08baff4fef", "aarti", 1);
INSERT INTO game_history VALUES ("02fb4749-3556-4196-9b63-aa08baff4fef", "abaca", 0);
INSERT INTO games VALUES ("36c8c53d-140b-4c1d-a9a7-7b3d2e1629ad", "sissy", "john");
INSERT INTO game_states VALUES ("36c8c53d-140b-4c1d-a9a7-7b3d2e1629ad", 5, "won");
INSERT INTO game_history VALUES ("36c8c53d-140b-4c1d-a9a7-7b3d2e1629ad", "sissy", 5);
INSERT INTO games VALUES ("eafb38bd-4257-467b-817d-ae76f299f2d7", "humph", "john");
INSERT INTO game_states VALUES ("eafb38bd-4257-467b-817d-ae76f299f2d7", 5, "In Progress");
INSERT INTO game_history VALUES ("eafb38bd-4257-467b-817d-ae76f299f2d7", "bahus", 5);

COMMIT;