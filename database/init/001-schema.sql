CREATE TABLE meetings (
    meeting_id BIGINT PRIMARY KEY,
    meeting_date DATE NOT NULL,
    track_name TEXT NOT NULL
);

CREATE TABLE races (
    race_id BIGINT PRIMARY KEY,
    meeting_id BIGINT NOT NULL REFERENCES meetings (meeting_id),
    race_number SMALLINT,
    race_time TIME,
    race_class TEXT,
    race_distance NUMERIC(7, 2),
    race_type TEXT,
    race_handicap BOOLEAN,
    race_going INTEGER,
    race_win_time NUMERIC(6, 2)
);

CREATE TABLE greyhounds (
    dog_id BIGINT PRIMARY KEY,
    dog_name TEXT NOT NULL,
    dog_born VARCHAR(7),
    dog_sex TEXT,
    sire_name TEXT,
    dam_name TEXT,
    dog_origin TEXT
);

CREATE TABLE race_participations (
    race_id BIGINT NOT NULL REFERENCES races (race_id),
    dog_id BIGINT NOT NULL REFERENCES greyhounds (dog_id),
    trap_number SMALLINT NOT NULL,
    trap_handicap NUMERIC(7, 2),
    trainer_name TEXT,
    result_position SMALLINT,
    result_btn_distance TEXT,
    result_run_time NUMERIC(6, 2),
    result_adjusted_time NUMERIC(6, 2),
    result_sectional_time NUMERIC(6, 2),
    result_comment TEXT,
    result_dog_weight NUMERIC(5, 2),
    starting_price TEXT,
    CONSTRAINT pk_race_participations PRIMARY KEY (race_id, dog_id)
);

CREATE INDEX idx_races_meeting_id
    ON races (meeting_id);

CREATE INDEX idx_race_participations_dog_id
    ON race_participations (dog_id);