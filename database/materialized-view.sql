CREATE MATERIALIZED VIEW guests_per_ep AS
SELECT eg.ep_id, g.guest_name FROM public.rm_ep_guests eg
JOIN public.rm_guests g
	ON g.guest_id = eg.guest_id