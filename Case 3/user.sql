
CREATE TABLE users (
    user_id serial primary key not null,
    user_name varchar(32) unique,
	user_password varchar(64) not null,
	user_modified_on timestamp without time zone default now(),
    user_delete_ind boolean default false
);