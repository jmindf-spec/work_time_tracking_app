--
-- PostgreSQL database dump
--

\restrict 14sdE0QQpYNALv4jjaGYgIq0q9M7J7xnOLU9fVsMYSMQQjppC112zUB3peZRuzJ

-- Dumped from database version 18.1
-- Dumped by pg_dump version 18.1

-- Started on 2025-12-28 16:50:22

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 5028 (class 0 OID 16651)
-- Dependencies: 220
-- Data for Name: employees; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.employees (id, name, "position", salary, hours_worked) FROM stdin;
4	Сидорова Анна Сергеевна	Дизайнер	90000.00	0.00
2	Иванов Иван Иванович	Разработчик	100000.00	0.00
3	Петров Петр Петрович	Менеджер проектов	80000.00	40.00
6	Захаров Захар Захарович	Разработчик	110000.00	0.00
\.


--
-- TOC entry 5030 (class 0 OID 16661)
-- Dependencies: 222
-- Data for Name: projects; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.projects (id, title) FROM stdin;
1	Разработка веб-сайта компании
2	Мобильное приложение для клиентов
3	Внутренняя система учета времени
4	Обновление CRM системы
\.


--
-- TOC entry 5032 (class 0 OID 16670)
-- Dependencies: 224
-- Data for Name: tasks; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tasks (id, title, description, status, hours_required, employee_id, project_id, hours_actual) FROM stdin;
15	Интеграция с платежной системой	Настроить интеграцию с PayPal	В процессе	30.00	\N	4	0.00
13	Тестирование функционала	Протестировать основной функционал приложения	Завершено	15.00	2	2	0.00
11	Дизайн главной страницы	Создать современный макет главной страницы	В процессе	40.00	2	1	0.00
12	Разработка API	Реализовать backend API для веб-сайта	Завершено	40.00	3	1	40.00
14	Создание базы данных	Разработать структуру БД для системы учета	Завершено	25.00	6	3	0.00
\.


--
-- TOC entry 5042 (class 0 OID 0)
-- Dependencies: 219
-- Name: employees_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.employees_id_seq', 6, true);


--
-- TOC entry 5043 (class 0 OID 0)
-- Dependencies: 221
-- Name: projects_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.projects_id_seq', 4, true);


--
-- TOC entry 5044 (class 0 OID 0)
-- Dependencies: 223
-- Name: tasks_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tasks_id_seq', 15, true);


-- Completed on 2025-12-28 16:50:23

--
-- PostgreSQL database dump complete
--

\unrestrict 14sdE0QQpYNALv4jjaGYgIq0q9M7J7xnOLU9fVsMYSMQQjppC112zUB3peZRuzJ

