CREATE TABLE IF NOT EXISTS public.rm_episodes(
    ep_id bigint,
    aired_date date,
    title text,
    teams text[],
    mission text,
    results text,
    PRIMARY KEY (ep_id)
);

CREATE TABLE IF NOT EXISTS public.rm_guests(
    guest_id bigint,
    guest_name character varying,
    PRIMARY KEY (guest_id)
);

-- junction table to keep track of guests in an episode
CREATE TABLE IF NOT EXISTS public.rm_ep_guests(
    ep_id bigint,
    guest_id bigint,
    PRIMARY KEY (ep_id, guest_id),
    FOREIGN KEY (guest_id)
        REFERENCES public.rm_guests (guest_id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (ep_id)
        REFERENCES public.rm_episodes (ep_id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

-- rating types e.g good, so-so, not good
CREATE TABLE IF NOT EXISTS public.rm_rating(
    id bigint,
    type character varying,
    PRIMARY KEY (id)
);

-- stores user watchlist items
CREATE TABLE IF NOT EXISTS public.rm_watchlist(
    id bigint NOT NULL,
    ep_id bigint,
    watched character varying,
    rating bigint,
    PRIMARY KEY (id),
    UNIQUE (ep_id),
    FOREIGN KEY (rating)
        REFERENCES public.rm_rating (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    FOREIGN KEY (ep_id)
        REFERENCES public.rm_episodes (ep_id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
);