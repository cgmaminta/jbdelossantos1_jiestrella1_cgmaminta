CREATE TABLE languages (
    language_id serial primary key not null,
    language_name varchar(70) unique,
    language_modified_date timestamp without time zone default now(),
    language_delete_ind boolean default false
);

INSERT INTO languages(language_id, language_name)
VALUES 
	(1, 'English'),
	(2, 'Filipino'),
	(3, 'Bisaya'),
	(4, 'Japanese'),
	(5, 'Korean'),
	(6, 'Chinese');

ALTER TABLE movies
ADD language_id int references languages(language_id)

UPDATE movies
SET language_id = 3
WHERE 1=1;
