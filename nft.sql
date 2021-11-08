--
-- PostgreSQL database dump
--

-- Dumped from database version 10.16 (Ubuntu 10.16-0ubuntu0.18.04.1)
-- Dumped by pg_dump version 10.16 (Ubuntu 10.16-0ubuntu0.18.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: auctionclosed; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.auctionclosed (
    id integer NOT NULL,
    "timestamp" bigint,
    auctionid bigint,
    closedstate bigint,
    fromaddress character varying(66),
    txhash character varying(66)
);


ALTER TABLE public.auctionclosed OWNER TO postgres;

--
-- Name: auctionclosed_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.auctionclosed_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auctionclosed_id_seq OWNER TO postgres;

--
-- Name: auctionclosed_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.auctionclosed_id_seq OWNED BY public.auctionclosed.id;


--
-- Name: auctioncreated; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.auctioncreated (
    id integer NOT NULL,
    "timestamp" bigint,
    auctionid bigint,
    seller character varying(66),
    itemaddress character varying(66),
    itemid bigint,
    auctiontype bigint,
    fromaddress character varying(66),
    txhash character varying(66)
);


ALTER TABLE public.auctioncreated OWNER TO postgres;

--
-- Name: auctioncreated_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.auctioncreated_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auctioncreated_id_seq OWNER TO postgres;

--
-- Name: auctioncreated_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.auctioncreated_id_seq OWNED BY public.auctioncreated.id;


--
-- Name: auctionlog; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.auctionlog (
    id integer NOT NULL,
    "timestamp" bigint,
    seller character varying(66),
    itemaddress character varying(66),
    itemid bigint,
    auctiontype bigint,
    auctionid bigint,
    bidder character varying(66),
    bidid bigint,
    amount numeric DEFAULT 0,
    auctionstate bigint DEFAULT 0,
    bidstate bigint DEFAULT 0,
    fromaddress character varying(66),
    eventtype character varying(66),
    txhash character varying(66)
);


ALTER TABLE public.auctionlog OWNER TO postgres;

--
-- Name: auctionlog_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.auctionlog_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auctionlog_id_seq OWNER TO postgres;

--
-- Name: auctionlog_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.auctionlog_id_seq OWNED BY public.auctionlog.id;


--
-- Name: auctionstatus; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.auctionstatus (
    "timestamp" bigint,
    id integer NOT NULL,
    auctiontype bigint,
    seller character varying(64),
    buyer character varying(64),
    itemaddress character varying(66),
    itemid bigint,
    startingprice numeric DEFAULT 0,
    amount numeric DEFAULT 0,
    auctionid bigint,
    status bigint,
    txhash character varying(66)
);


ALTER TABLE public.auctionstatus OWNER TO postgres;

--
-- Name: auctionstatus_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.auctionstatus_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auctionstatus_id_seq OWNER TO postgres;

--
-- Name: auctionstatus_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.auctionstatus_id_seq OWNED BY public.auctionstatus.id;


--
-- Name: banner_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.banner_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.banner_id_seq OWNER TO postgres;

--
-- Name: banner; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.banner (
    id integer DEFAULT nextval('public.banner_id_seq'::regclass) NOT NULL,
    uri character varying(255),
    adddate timestamp(6) without time zone,
    type character varying
);


ALTER TABLE public.banner OWNER TO postgres;

--
-- Name: bidactivated; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.bidactivated (
    id integer NOT NULL,
    "timestamp" bigint,
    auctionid bigint,
    bidid bigint,
    fromaddress character varying(66),
    txhash character varying(66)
);


ALTER TABLE public.bidactivated OWNER TO postgres;

--
-- Name: bidactivated_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.bidactivated_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.bidactivated_id_seq OWNER TO postgres;

--
-- Name: bidactivated_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.bidactivated_id_seq OWNED BY public.bidactivated.id;


--
-- Name: bidcreated; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.bidcreated (
    id integer NOT NULL,
    "timestamp" bigint,
    bidder character varying(66),
    auctionid bigint,
    bidid bigint,
    amount numeric DEFAULT 0,
    fromaddress character varying(66),
    txhash character varying(66)
);


ALTER TABLE public.bidcreated OWNER TO postgres;

--
-- Name: bidcreated_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.bidcreated_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.bidcreated_id_seq OWNER TO postgres;

--
-- Name: bidcreated_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.bidcreated_id_seq OWNED BY public.bidcreated.id;


--
-- Name: biddeactivated; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.biddeactivated (
    id integer NOT NULL,
    "timestamp" bigint,
    auctionid bigint,
    bidid bigint,
    newbidstate bigint,
    fromaddress character varying(66),
    txhash character varying(66)
);


ALTER TABLE public.biddeactivated OWNER TO postgres;

--
-- Name: biddeactivated_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.biddeactivated_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.biddeactivated_id_seq OWNER TO postgres;

--
-- Name: biddeactivated_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.biddeactivated_id_seq OWNED BY public.biddeactivated.id;


--
-- Name: bidstatus; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.bidstatus (
    id integer NOT NULL,
    bidder character varying(64),
    auctionid bigint,
    bidid bigint,
    bidamount numeric DEFAULT 0,
    status bigint DEFAULT 0
);


ALTER TABLE public.bidstatus OWNER TO postgres;

--
-- Name: bidstatus_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.bidstatus_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.bidstatus_id_seq OWNER TO postgres;

--
-- Name: bidstatus_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.bidstatus_id_seq OWNED BY public.bidstatus.id;


--
-- Name: collectioninfo_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.collectioninfo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.collectioninfo_id_seq OWNER TO postgres;

--
-- Name: collectioninfo; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.collectioninfo (
    owner character varying(66),
    title character varying(128),
    uri character varying(256),
    description text,
    createdate timestamp without time zone,
    status integer,
    shorturi character varying,
    id integer DEFAULT nextval('public.collectioninfo_id_seq'::regclass) NOT NULL
);


ALTER TABLE public.collectioninfo OWNER TO postgres;

--
-- Name: featured; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.featured (
    id integer NOT NULL,
    itemaddress character varying(66),
    title character varying(256),
    name character varying(256),
    image character varying(256),
    description text,
    activate bigint DEFAULT 0
);


ALTER TABLE public.featured OWNER TO postgres;

--
-- Name: featured_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.featured_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.featured_id_seq OWNER TO postgres;

--
-- Name: featured_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.featured_id_seq OWNED BY public.featured.id;


--
-- Name: marketfeescollected; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.marketfeescollected (
    id integer NOT NULL,
    "timestamp" bigint,
    collectingmanager character varying(66),
    amountcollected numeric DEFAULT 0,
    fromaddress character varying(66),
    txhash character varying(66)
);


ALTER TABLE public.marketfeescollected OWNER TO postgres;

--
-- Name: marketfeescollected_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.marketfeescollected_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.marketfeescollected_id_seq OWNER TO postgres;

--
-- Name: marketfeescollected_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.marketfeescollected_id_seq OWNED BY public.marketfeescollected.id;


--
-- Name: marketfeeupdate; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.marketfeeupdate (
    id integer NOT NULL,
    "timestamp" bigint,
    param bigint,
    oldvalue bigint,
    newvalue bigint,
    fromaddress character varying(66),
    txhash character varying(66)
);


ALTER TABLE public.marketfeeupdate OWNER TO postgres;

--
-- Name: marketfeeupdate_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.marketfeeupdate_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.marketfeeupdate_id_seq OWNER TO postgres;

--
-- Name: marketfeeupdate_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.marketfeeupdate_id_seq OWNED BY public.marketfeeupdate.id;


--
-- Name: marketttlupdate; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.marketttlupdate (
    id integer NOT NULL,
    "timestamp" bigint,
    oldvalue bigint,
    newvalue bigint,
    fromaddress character varying(66),
    txhash character varying(66)
);


ALTER TABLE public.marketttlupdate OWNER TO postgres;

--
-- Name: marketttlupdate_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.marketttlupdate_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.marketttlupdate_id_seq OWNER TO postgres;

--
-- Name: marketttlupdate_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.marketttlupdate_id_seq OWNED BY public.marketttlupdate.id;


--
-- Name: nft_registration; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.nft_registration (
    nftaddr character varying(66) NOT NULL,
    type bigint DEFAULT 0,
    confirmed bigint DEFAULT 0,
    flag bigint DEFAULT 0,
    category bigint DEFAULT 0,
    description character varying(256)
);


ALTER TABLE public.nft_registration OWNER TO postgres;

--
-- Name: nftarticle; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.nftarticle (
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    article character varying(256),
    title character varying(256),
    image character varying(256),
    contents text,
    activate bigint
);


ALTER TABLE public.nftarticle OWNER TO postgres;

--
-- Name: nftarticle_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.nftarticle_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.nftarticle_id_seq OWNER TO postgres;

--
-- Name: nftarticle_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.nftarticle_id_seq OWNED BY public.nftarticle.id;


--
-- Name: nftcreated; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.nftcreated (
    id integer NOT NULL,
    "timestamp" bigint,
    nftid bigint,
    nftcontract character varying(66),
    creator character varying(66),
    fromaddress character varying(66),
    txhash character varying(66)
);


ALTER TABLE public.nftcreated OWNER TO postgres;

--
-- Name: nftcreated_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.nftcreated_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.nftcreated_id_seq OWNER TO postgres;

--
-- Name: nftcreated_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.nftcreated_id_seq OWNED BY public.nftcreated.id;


--
-- Name: nftevent; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.nftevent (
    "timestamp" bigint,
    _from character varying(66),
    _to character varying(66),
    id bigint,
    approved boolean,
    uri character varying(256),
    fromaddress character varying(66),
    txhash character varying(66),
    eventtype character varying(66)
);


ALTER TABLE public.nftevent OWNER TO postgres;

--
-- Name: nftinfo; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.nftinfo (
    id integer NOT NULL,
    owner character varying(66),
    nftname character varying(128),
    nftsymbol character varying(64),
    nftaddress character varying(66),
    nftid bigint,
    title character varying(128),
    category character varying(128),
    uri character varying(256),
    image character varying(256),
    description text,
    metadata text,
    regdate timestamp without time zone,
    collectionid integer
);


ALTER TABLE public.nftinfo OWNER TO postgres;

--
-- Name: nftinfo_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.nftinfo_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.nftinfo_id_seq OWNER TO postgres;

--
-- Name: nftinfo_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.nftinfo_id_seq OWNED BY public.nftinfo.id;


--
-- Name: royaltycollected; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.royaltycollected (
    id integer NOT NULL,
    "timestamp" bigint,
    beneficiary character varying(66),
    amountcollected numeric DEFAULT 0,
    fromaddress character varying(66),
    txhash character varying(66)
);


ALTER TABLE public.royaltycollected OWNER TO postgres;

--
-- Name: royaltycollected_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.royaltycollected_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.royaltycollected_id_seq OWNER TO postgres;

--
-- Name: royaltycollected_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.royaltycollected_id_seq OWNED BY public.royaltycollected.id;


--
-- Name: userinfo; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.userinfo (
    account character varying(66) NOT NULL,
    name character varying(64) DEFAULT 'Unnamed'::character varying NOT NULL,
    email character varying(64),
    introduction text,
    signature character varying(256),
    logindate timestamp without time zone,
    regdate timestamp without time zone,
    updatedate timestamp without time zone,
    isadmin integer
);


ALTER TABLE public.userinfo OWNER TO postgres;

--
-- Name: auctionclosed id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auctionclosed ALTER COLUMN id SET DEFAULT nextval('public.auctionclosed_id_seq'::regclass);


--
-- Name: auctioncreated id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auctioncreated ALTER COLUMN id SET DEFAULT nextval('public.auctioncreated_id_seq'::regclass);


--
-- Name: auctionlog id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auctionlog ALTER COLUMN id SET DEFAULT nextval('public.auctionlog_id_seq'::regclass);


--
-- Name: auctionstatus id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auctionstatus ALTER COLUMN id SET DEFAULT nextval('public.auctionstatus_id_seq'::regclass);


--
-- Name: bidactivated id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bidactivated ALTER COLUMN id SET DEFAULT nextval('public.bidactivated_id_seq'::regclass);


--
-- Name: bidcreated id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bidcreated ALTER COLUMN id SET DEFAULT nextval('public.bidcreated_id_seq'::regclass);


--
-- Name: biddeactivated id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.biddeactivated ALTER COLUMN id SET DEFAULT nextval('public.biddeactivated_id_seq'::regclass);


--
-- Name: bidstatus id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bidstatus ALTER COLUMN id SET DEFAULT nextval('public.bidstatus_id_seq'::regclass);


--
-- Name: featured id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.featured ALTER COLUMN id SET DEFAULT nextval('public.featured_id_seq'::regclass);


--
-- Name: marketfeescollected id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.marketfeescollected ALTER COLUMN id SET DEFAULT nextval('public.marketfeescollected_id_seq'::regclass);


--
-- Name: marketfeeupdate id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.marketfeeupdate ALTER COLUMN id SET DEFAULT nextval('public.marketfeeupdate_id_seq'::regclass);


--
-- Name: marketttlupdate id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.marketttlupdate ALTER COLUMN id SET DEFAULT nextval('public.marketttlupdate_id_seq'::regclass);


--
-- Name: nftarticle id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.nftarticle ALTER COLUMN id SET DEFAULT nextval('public.nftarticle_id_seq'::regclass);


--
-- Name: nftcreated id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.nftcreated ALTER COLUMN id SET DEFAULT nextval('public.nftcreated_id_seq'::regclass);


--
-- Name: nftinfo id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.nftinfo ALTER COLUMN id SET DEFAULT nextval('public.nftinfo_id_seq'::regclass);


--
-- Name: royaltycollected id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.royaltycollected ALTER COLUMN id SET DEFAULT nextval('public.royaltycollected_id_seq'::regclass);


--
-- Data for Name: auctionclosed; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.auctionclosed (id, "timestamp", auctionid, closedstate, fromaddress, txhash) FROM stdin;
\.


--
-- Data for Name: auctioncreated; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.auctioncreated (id, "timestamp", auctionid, seller, itemaddress, itemid, auctiontype, fromaddress, txhash) FROM stdin;
\.


--
-- Data for Name: auctionlog; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.auctionlog (id, "timestamp", seller, itemaddress, itemid, auctiontype, auctionid, bidder, bidid, amount, auctionstate, bidstate, fromaddress, eventtype, txhash) FROM stdin;
1	1620784260	0x4Bd2e2279AC50A7114d4DD003f411cd040158db9	0xA10527125088f2d033Afa3A98B256d844f7dD864	0	0	0	\N	\N	100000000000000000	0	0	0x4Bd2e2279AC50A7114d4DD003f411cd040158db9	AuctionCreated	0x643D512A71CF3FBCBD016D9C4AD8F9819662B168CE57934428C8752A9641ABF2
2	1621229536	\N	\N	\N	\N	0	0xa342F0d01b65a75437A20EA84DB4FF0c212336fa	0	100000000000000000	0	0	0xa342F0d01b65a75437A20EA84DB4FF0c212336fa	BidCreated	0x7B8D173D63B60228AFD97A2475D518812EA037EEBCC89CA6480D54DD63654B3D
3	1621229536	0x4Bd2e2279AC50A7114d4DD003f411cd040158db9	\N	\N	\N	0	\N	0	100000000000000000	0	0	0xa342F0d01b65a75437A20EA84DB4FF0c212336fa	BidActivated	0x7B8D173D63B60228AFD97A2475D518812EA037EEBCC89CA6480D54DD63654B3D
4	1621229536	\N	\N	\N	\N	0	\N	0	0	0	2	0xa342F0d01b65a75437A20EA84DB4FF0c212336fa	BidDeactivated	0x7B8D173D63B60228AFD97A2475D518812EA037EEBCC89CA6480D54DD63654B3D
5	1621229536	\N	\N	\N	\N	0	\N	\N	0	1	0	0xa342F0d01b65a75437A20EA84DB4FF0c212336fa	AuctionClosed	0x7B8D173D63B60228AFD97A2475D518812EA037EEBCC89CA6480D54DD63654B3D
8	1627540816	0x4Bd2e2279AC50A7114d4DD003f411cd040158db9	0xA10527125088f2d033Afa3A98B256d844f7dD864	1	0	1	\N	\N	1000000000000000	0	0	0x4Bd2e2279AC50A7114d4DD003f411cd040158db9	AuctionCreated	0x0FA985747C701B705D2A4F9497BFDC722299F3BDB20A48F5F85EEBB2BF4DB5BC
10	1627866969	0x4Bd2e2279AC50A7114d4DD003f411cd040158db9	0xA10527125088f2d033Afa3A98B256d844f7dD864	3	0	2	\N	\N	500000000000000000	0	0	0x4Bd2e2279AC50A7114d4DD003f411cd040158db9	AuctionCreated	0xE98D83755B93D101C1604D328E1017C18B9BFA6CEB54B36D5827A0B8CCD1A52F
11	1627866969	0x4Bd2e2279AC50A7114d4DD003f411cd040158db9	0xA10527125088f2d033Afa3A98B256d844f7dD864	3	0	2	\N	\N	500000000000000000	0	0	0x4Bd2e2279AC50A7114d4DD003f411cd040158db9	AuctionCreated	0xE98D83755B93D101C1604D328E1017C18B9BFA6CEB54B36D5827A0B8CCD1A52F
\.


--
-- Data for Name: auctionstatus; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.auctionstatus ("timestamp", id, auctiontype, seller, buyer, itemaddress, itemid, startingprice, amount, auctionid, status, txhash) FROM stdin;
1621229536	1	0	0x4Bd2e2279AC50A7114d4DD003f411cd040158db9	0xa342F0d01b65a75437A20EA84DB4FF0c212336fa	0xA10527125088f2d033Afa3A98B256d844f7dD864	0	100000000000000000	100000000000000000	0	1	0x7B8D173D63B60228AFD97A2475D518812EA037EEBCC89CA6480D54DD63654B3D
\N	2	0	0x4Bd2e2279AC50A7114d4DD003f411cd040158db9	\N	0xA10527125088f2d033Afa3A98B256d844f7dD864	0	100000000000000000	0	0	0	0x643D512A71CF3FBCBD016D9C4AD8F9819662B168CE57934428C8752A9641ABF2
\N	4	0	0x4Bd2e2279AC50A7114d4DD003f411cd040158db9	\N	0xA10527125088f2d033Afa3A98B256d844f7dD864	1	1000000000000000	0	1	0	0x0FA985747C701B705D2A4F9497BFDC722299F3BDB20A48F5F85EEBB2BF4DB5BC
\N	6	0	0x4Bd2e2279AC50A7114d4DD003f411cd040158db9	\N	0xA10527125088f2d033Afa3A98B256d844f7dD864	3	500000000000000000	0	2	0	0xE98D83755B93D101C1604D328E1017C18B9BFA6CEB54B36D5827A0B8CCD1A52F
\N	7	0	0x4Bd2e2279AC50A7114d4DD003f411cd040158db9	\N	0xA10527125088f2d033Afa3A98B256d844f7dD864	3	500000000000000000	0	2	0	0xE98D83755B93D101C1604D328E1017C18B9BFA6CEB54B36D5827A0B8CCD1A52F
\.


--
-- Data for Name: banner; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.banner (id, uri, adddate, type) FROM stdin;
1	https://ipfs.infura.io/ipfs/QmaTkPy9iuoeWeGn6zMnJEdxd3h1c7JEhPmeUd4NaTGp2M	2021-07-27 19:54:05.890062	left
2	https://ipfs.infura.io/ipfs/QmSAHEv7XPK63EAw7gHDwAvozcCcDBio5UFSeMrkKKYQoN	2021-07-27 19:59:29.447334	left
8	https://ipfs.infura.io/ipfs/QmdLhhcewzS29knN7ZciRGpaJSNJxAWHgpbtrFpDniTkUJ	2021-07-27 20:20:12.653574	right
10	https://ipfs.infura.io/ipfs/QmSNJsbe1789GQJZhyrjejeFaCEbKBhzpzxDgy67toFcLj	2021-07-27 20:20:44.223158	right
9	https://ipfs.infura.io/ipfs/QmVfsGwHNjLoSWrAZDJJNzRv54LmjjghoRW8rmZcfqq1z8	2021-07-27 20:20:28.081335	right
6	https://ipfs.infura.io/ipfs/QmXfhSd9A8WJjPj5utuXvRw2UivBVKPfUD67CUA63wupAd	2021-07-27 20:17:13.700587	left
\.


--
-- Data for Name: bidactivated; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.bidactivated (id, "timestamp", auctionid, bidid, fromaddress, txhash) FROM stdin;
\.


--
-- Data for Name: bidcreated; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.bidcreated (id, "timestamp", bidder, auctionid, bidid, amount, fromaddress, txhash) FROM stdin;
\.


--
-- Data for Name: biddeactivated; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.biddeactivated (id, "timestamp", auctionid, bidid, newbidstate, fromaddress, txhash) FROM stdin;
\.


--
-- Data for Name: bidstatus; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.bidstatus (id, bidder, auctionid, bidid, bidamount, status) FROM stdin;
1	0xa342F0d01b65a75437A20EA84DB4FF0c212336fa	0	0	100000000000000000	1
\.


--
-- Data for Name: collectioninfo; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.collectioninfo (owner, title, uri, description, createdate, status, shorturi, id) FROM stdin;
0x4Bd2e2279AC50A7114d4DD003f411cd040158db9	POSHGIRLS	https://ipfs.infura.io/ipfs/QmcaX5gMnbARp2q7kRpKSaWDgUPTevaPWKJtohEMYiGzPj	The ZenithX Project, which started in February, started a global audition from its Korean partner, Number One Media, and as a result of the final audition, it consisted of 4 members each from Korea and Japan. The strategic partner, Number One Media, has produced popular idol groups LIPBUBBLE, WANNA.B, Z-Boys, and Z-Girls.	2021-07-29 06:15:21.303171	1	poshgirls	4
\.


--
-- Data for Name: featured; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.featured (id, itemaddress, title, name, image, description, activate) FROM stdin;
1	0xf9DA22988D9645d89E3fE2f4ae6DaF5594aE6014	NFT Hub X Hiro Yamagata Part #1	Hiro Yamagata	https://zenxhub.zenithx.co/ad.jpg	Buy the ownership of Hiro Yamagata’s artwork as NFT	1
2	0xf9DA22988D9645d89E3fE2f4ae6DaF5594aE6014	NFT Hub X Hiro Yamagata Part #2	Hiro Yamagata	https://zenxhub.zenithx.co/ad.jpg	Buy the ownership of Hiro Yamagata’s artwork as NFT	1
\.


--
-- Data for Name: marketfeescollected; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.marketfeescollected (id, "timestamp", collectingmanager, amountcollected, fromaddress, txhash) FROM stdin;
\.


--
-- Data for Name: marketfeeupdate; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.marketfeeupdate (id, "timestamp", param, oldvalue, newvalue, fromaddress, txhash) FROM stdin;
\.


--
-- Data for Name: marketttlupdate; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.marketttlupdate (id, "timestamp", oldvalue, newvalue, fromaddress, txhash) FROM stdin;
\.


--
-- Data for Name: nft_registration; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.nft_registration (nftaddr, type, confirmed, flag, category, description) FROM stdin;
0x3a8778a58993ba4b941f85684d74750043a4bb5f	999	0	0	1	\N
0x6c94954d0b265f657a4a1b35dfaa8b73d1a3f199	999	0	0	1	\N
\.


--
-- Data for Name: nftarticle; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.nftarticle (id, created_at, article, title, image, contents, activate) FROM stdin;
\.


--
-- Data for Name: nftcreated; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.nftcreated (id, "timestamp", nftid, nftcontract, creator, fromaddress, txhash) FROM stdin;
\.


--
-- Data for Name: nftevent; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.nftevent ("timestamp", _from, _to, id, approved, uri, fromaddress, txhash, eventtype) FROM stdin;
1621229536	0xe04cA7DD6f34fDD5F1D7C4247D1723c033E65F1F	0x0000000000000000000000000000000000000000	0	\N	\N	0xa342F0d01b65a75437A20EA84DB4FF0c212336fa	0x7B8D173D63B60228AFD97A2475D518812EA037EEBCC89CA6480D54DD63654B3D	Approval
1621229536	0xe04cA7DD6f34fDD5F1D7C4247D1723c033E65F1F	0xa342F0d01b65a75437A20EA84DB4FF0c212336fa	0	\N	\N	0xa342F0d01b65a75437A20EA84DB4FF0c212336fa	0x7B8D173D63B60228AFD97A2475D518812EA037EEBCC89CA6480D54DD63654B3D	Transfer
1627540723	0x0000000000000000000000000000000000000000	0x4Bd2e2279AC50A7114d4DD003f411cd040158db9	1	\N	\N	0x4Bd2e2279AC50A7114d4DD003f411cd040158db9	0x1019354EFA323A6D3052D895D49333C26248076ED2DC9CD189914472476C960F	Transfer
1627540816	0x4Bd2e2279AC50A7114d4DD003f411cd040158db9	0x0000000000000000000000000000000000000000	1	\N	\N	0x4Bd2e2279AC50A7114d4DD003f411cd040158db9	0x0FA985747C701B705D2A4F9497BFDC722299F3BDB20A48F5F85EEBB2BF4DB5BC	Approval
1627540816	0x4Bd2e2279AC50A7114d4DD003f411cd040158db9	0xe04cA7DD6f34fDD5F1D7C4247D1723c033E65F1F	1	\N	\N	0x4Bd2e2279AC50A7114d4DD003f411cd040158db9	0x0FA985747C701B705D2A4F9497BFDC722299F3BDB20A48F5F85EEBB2BF4DB5BC	Transfer
1627540723	0x0000000000000000000000000000000000000000	0x4Bd2e2279AC50A7114d4DD003f411cd040158db9	1	\N	\N	0x4Bd2e2279AC50A7114d4DD003f411cd040158db9	0x1019354EFA323A6D3052D895D49333C26248076ED2DC9CD189914472476C960F	Transfer
1627540723	\N	\N	1	\N	https://ipfs.infura.io/ipfs/QmVSrriHik32V8wKv6KzE5PqXni18b52eEH9Fk1SQ7hTMo	0x4Bd2e2279AC50A7114d4DD003f411cd040158db9	0x1019354EFA323A6D3052D895D49333C26248076ED2DC9CD189914472476C960F	TokenURIUpdate
1627540816	0x4Bd2e2279AC50A7114d4DD003f411cd040158db9	0x0000000000000000000000000000000000000000	1	\N	\N	0x4Bd2e2279AC50A7114d4DD003f411cd040158db9	0x0FA985747C701B705D2A4F9497BFDC722299F3BDB20A48F5F85EEBB2BF4DB5BC	Approval
1627540816	0x4Bd2e2279AC50A7114d4DD003f411cd040158db9	0xe04cA7DD6f34fDD5F1D7C4247D1723c033E65F1F	1	\N	\N	0x4Bd2e2279AC50A7114d4DD003f411cd040158db9	0x0FA985747C701B705D2A4F9497BFDC722299F3BDB20A48F5F85EEBB2BF4DB5BC	Transfer
1627622782	0x0000000000000000000000000000000000000000	0x4Bd2e2279AC50A7114d4DD003f411cd040158db9	2	\N	\N	0x4Bd2e2279AC50A7114d4DD003f411cd040158db9	0x57B16FF05020A51E866BB412887DEC4D461036D0860F80DF7E7F5871DA4FD80F	Transfer
1627622782	\N	\N	2	\N	https://ipfs.infura.io/ipfs/QmWxscJ2GbWi3pFqhvC6fusQjGUyTiaEFqidUCU9NYegFd	0x4Bd2e2279AC50A7114d4DD003f411cd040158db9	0x57B16FF05020A51E866BB412887DEC4D461036D0860F80DF7E7F5871DA4FD80F	TokenURIUpdate
1627622782	0x0000000000000000000000000000000000000000	0x4Bd2e2279AC50A7114d4DD003f411cd040158db9	2	\N	\N	0x4Bd2e2279AC50A7114d4DD003f411cd040158db9	0x57B16FF05020A51E866BB412887DEC4D461036D0860F80DF7E7F5871DA4FD80F	Transfer
1627866714	0x0000000000000000000000000000000000000000	0x4Bd2e2279AC50A7114d4DD003f411cd040158db9	3	\N	\N	0x4Bd2e2279AC50A7114d4DD003f411cd040158db9	0xFD8E7BC5AA175B74CD745A087B4148FF899158CC2C4357F486CC02342487C050	Transfer
1627866714	\N	\N	3	\N	https://ipfs.infura.io/ipfs/QmNvVWc5u1EyodnvDC5Aj1p3ha7FX9y73vXJhHdGQTe9G7	0x4Bd2e2279AC50A7114d4DD003f411cd040158db9	0xFD8E7BC5AA175B74CD745A087B4148FF899158CC2C4357F486CC02342487C050	TokenURIUpdate
1627866969	0x4Bd2e2279AC50A7114d4DD003f411cd040158db9	0x0000000000000000000000000000000000000000	3	\N	\N	0x4Bd2e2279AC50A7114d4DD003f411cd040158db9	0xE98D83755B93D101C1604D328E1017C18B9BFA6CEB54B36D5827A0B8CCD1A52F	Approval
1627866969	0x4Bd2e2279AC50A7114d4DD003f411cd040158db9	0xe04cA7DD6f34fDD5F1D7C4247D1723c033E65F1F	3	\N	\N	0x4Bd2e2279AC50A7114d4DD003f411cd040158db9	0xE98D83755B93D101C1604D328E1017C18B9BFA6CEB54B36D5827A0B8CCD1A52F	Transfer
1627866969	0x4Bd2e2279AC50A7114d4DD003f411cd040158db9	0x0000000000000000000000000000000000000000	3	\N	\N	0x4Bd2e2279AC50A7114d4DD003f411cd040158db9	0xE98D83755B93D101C1604D328E1017C18B9BFA6CEB54B36D5827A0B8CCD1A52F	Approval
1627866969	0x4Bd2e2279AC50A7114d4DD003f411cd040158db9	0xe04cA7DD6f34fDD5F1D7C4247D1723c033E65F1F	3	\N	\N	0x4Bd2e2279AC50A7114d4DD003f411cd040158db9	0xE98D83755B93D101C1604D328E1017C18B9BFA6CEB54B36D5827A0B8CCD1A52F	Transfer
1627866714	0x0000000000000000000000000000000000000000	0x4Bd2e2279AC50A7114d4DD003f411cd040158db9	3	\N	\N	0x4Bd2e2279AC50A7114d4DD003f411cd040158db9	0xFD8E7BC5AA175B74CD745A087B4148FF899158CC2C4357F486CC02342487C050	Transfer
1627866969	0x4Bd2e2279AC50A7114d4DD003f411cd040158db9	0x0000000000000000000000000000000000000000	3	\N	\N	0x4Bd2e2279AC50A7114d4DD003f411cd040158db9	0xE98D83755B93D101C1604D328E1017C18B9BFA6CEB54B36D5827A0B8CCD1A52F	Approval
1627866969	0x4Bd2e2279AC50A7114d4DD003f411cd040158db9	0xe04cA7DD6f34fDD5F1D7C4247D1723c033E65F1F	3	\N	\N	0x4Bd2e2279AC50A7114d4DD003f411cd040158db9	0xE98D83755B93D101C1604D328E1017C18B9BFA6CEB54B36D5827A0B8CCD1A52F	Transfer
\.


--
-- Data for Name: nftinfo; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.nftinfo (id, owner, nftname, nftsymbol, nftaddress, nftid, title, category, uri, image, description, metadata, regdate, collectionid) FROM stdin;
1	0xe04cA7DD6f34fDD5F1D7C4247D1723c033E65F1F	Zenx	NFT0	0xA10527125088f2d033Afa3A98B256d844f7dD864	0	zenithX first block creation	1	https://ipfs.infura.io/ipfs/QmYHU4EnrhhfvrJLxb1NmBR3vdW3VTsjHkCQntzFeEyBVW	https://ipfs.infura.io/ipfs/QmfAiQrEGQnguK8GT4d7uVRCC3cRo526uQ6LPVfCtuivdn	The first block created on the zenithX platform, ZENX	\N	2021-05-12 01:18:18.858671	\N
2	0xe04cA7DD6f34fDD5F1D7C4247D1723c033E65F1F	Zenithx.eth	NFT0	0xA10527125088f2d033Afa3A98B256d844f7dD864	1	POSHPART	1	https://ipfs.infura.io/ipfs/QmVSrriHik32V8wKv6KzE5PqXni18b52eEH9Fk1SQ7hTMo	https://ipfs.infura.io/ipfs/QmcPTSF7DmuLxFusqWnpAUyBk9ywZmUJGoLmEhtsk6Pn5t	Your idea deserves to be heard. This product will help you turns ideas into persuasive presentations to communicate your messages clearly, meet your goals, and exceed expectations in everything from thought leadership and sales to everyday employee communication.	\N	2021-07-29 06:38:51.8374	4
3	0xe04cA7DD6f34fDD5F1D7C4247D1723c033E65F1F	Zenithx.eth	NFT0	0xA10527125088f2d033Afa3A98B256d844f7dD864	3	lalalalalalalalalalalal	1	https://ipfs.infura.io/ipfs/QmNvVWc5u1EyodnvDC5Aj1p3ha7FX9y73vXJhHdGQTe9G7	https://ipfs.infura.io/ipfs/QmXttZepnq8XTR5jTP5V5dqv56ytRSygkY89erPChuER3m	lalalalalalalalalalalal	\N	2021-08-02 01:12:13.37952	4
\.


--
-- Data for Name: royaltycollected; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.royaltycollected (id, "timestamp", beneficiary, amountcollected, fromaddress, txhash) FROM stdin;
\.


--
-- Data for Name: userinfo; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.userinfo (account, name, email, introduction, signature, logindate, regdate, updatedate, isadmin) FROM stdin;
0x7806Cedb032eC41147966019Da90D09d2fCd1E36	Noname				2021-07-12 14:55:08.693774	2021-05-11 08:51:35.305784	\N	0
0x8d79d34FeA4322FF63A2394da1AE8b581C3Ab230	Noname				2021-07-19 02:56:31.705866	2021-07-19 02:55:45.040676	\N	0
0x7B8A779560Ae42d154B127eEefAfeD10A71A9c01	Noname				2021-04-29 07:12:16.729444	2021-04-29 07:12:16.066846	\N	0
0x5Ee8F42580eBe67146fA6bBABd9DF1e5e8477A37	ZenithX		Zenith X content manage official 		2021-05-01 02:18:18.013813	2021-04-29 06:12:00.989898	2021-04-29 06:13:49.478761	0
0x53DF47c54d94C2EbE41cb1FBeEfa4AAD51178B79	Noname				2021-05-11 09:14:34.520652	2021-05-09 16:11:44.365412	\N	0
0x4cE5cC2Eb4470375819Ff2F979a3973a2e671198	Noname				2021-05-04 06:51:48.488463	2021-05-04 03:09:52.422182	\N	0
0xa342F0d01b65a75437A20EA84DB4FF0c212336fa	nahees		my age is 8		2021-07-22 10:53:20.541553	2021-04-26 10:20:36.645003	2021-05-20 11:38:09.597014	0
0x4Bd2e2279AC50A7114d4DD003f411cd040158db9	Zenithx.eth		Zenith X official		2021-08-13 09:56:05.818994	2021-04-27 10:03:34.855274	2021-07-29 01:36:45.161366	1
0x45840E6b8b7578B80838cd71301027812dc2B9f5	Noname				2021-08-17 08:14:13.172599	2021-07-29 03:06:54.605704	\N	0
0xfc1779a245455f43Cd2F974fB22Fbf051F213c5d	CiCi				2021-09-09 03:17:59.600168	2021-07-25 00:24:29.868452	2021-07-28 01:31:53.665305	1
0x8CC0e858aFFC185AdE43F7D63917E63cDAB50e46	Noname				2021-07-29 02:36:25.904875	2021-05-10 06:02:31.815473	\N	0
0xe17FEb09049c6d526402972978B80efC791fe927	Noname				2021-05-04 06:28:29.863924	2021-05-04 06:06:14.885785	\N	0
0x509efC273f084e850B88DCdc8651dD2836900140	Noname				2021-07-05 09:25:33.456209	2021-07-05 09:25:32.181146	\N	0
\.


--
-- Name: auctionclosed_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.auctionclosed_id_seq', 1, false);


--
-- Name: auctioncreated_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.auctioncreated_id_seq', 1, false);


--
-- Name: auctionlog_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.auctionlog_id_seq', 11, true);


--
-- Name: auctionstatus_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.auctionstatus_id_seq', 7, true);


--
-- Name: banner_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.banner_id_seq', 12, true);


--
-- Name: bidactivated_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.bidactivated_id_seq', 1, false);


--
-- Name: bidcreated_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.bidcreated_id_seq', 1, false);


--
-- Name: biddeactivated_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.biddeactivated_id_seq', 1, false);


--
-- Name: bidstatus_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.bidstatus_id_seq', 1, true);


--
-- Name: collectioninfo_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.collectioninfo_id_seq', 4, true);


--
-- Name: featured_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.featured_id_seq', 2, true);


--
-- Name: marketfeescollected_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.marketfeescollected_id_seq', 1, false);


--
-- Name: marketfeeupdate_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.marketfeeupdate_id_seq', 1, false);


--
-- Name: marketttlupdate_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.marketttlupdate_id_seq', 1, false);


--
-- Name: nftarticle_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.nftarticle_id_seq', 1, false);


--
-- Name: nftcreated_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.nftcreated_id_seq', 1, false);


--
-- Name: nftinfo_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.nftinfo_id_seq', 3, true);


--
-- Name: royaltycollected_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.royaltycollected_id_seq', 1, false);


--
-- Name: auctionclosed auctionclosed_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auctionclosed
    ADD CONSTRAINT auctionclosed_pkey PRIMARY KEY (id);


--
-- Name: auctioncreated auctioncreated_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auctioncreated
    ADD CONSTRAINT auctioncreated_pkey PRIMARY KEY (id);


--
-- Name: auctionlog auctionlog_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auctionlog
    ADD CONSTRAINT auctionlog_pkey PRIMARY KEY (id);


--
-- Name: auctionstatus auctionstatus_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auctionstatus
    ADD CONSTRAINT auctionstatus_pkey PRIMARY KEY (id);


--
-- Name: banner banner_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.banner
    ADD CONSTRAINT banner_pkey PRIMARY KEY (id);


--
-- Name: bidactivated bidactivated_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bidactivated
    ADD CONSTRAINT bidactivated_pkey PRIMARY KEY (id);


--
-- Name: bidcreated bidcreated_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bidcreated
    ADD CONSTRAINT bidcreated_pkey PRIMARY KEY (id);


--
-- Name: biddeactivated biddeactivated_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.biddeactivated
    ADD CONSTRAINT biddeactivated_pkey PRIMARY KEY (id);


--
-- Name: bidstatus bidstatus_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bidstatus
    ADD CONSTRAINT bidstatus_pkey PRIMARY KEY (id);


--
-- Name: featured featured_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.featured
    ADD CONSTRAINT featured_pkey PRIMARY KEY (id);


--
-- Name: marketfeescollected marketfeescollected_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.marketfeescollected
    ADD CONSTRAINT marketfeescollected_pkey PRIMARY KEY (id);


--
-- Name: marketfeeupdate marketfeeupdate_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.marketfeeupdate
    ADD CONSTRAINT marketfeeupdate_pkey PRIMARY KEY (id);


--
-- Name: marketttlupdate marketttlupdate_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.marketttlupdate
    ADD CONSTRAINT marketttlupdate_pkey PRIMARY KEY (id);


--
-- Name: nft_registration nft_registration_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.nft_registration
    ADD CONSTRAINT nft_registration_pkey PRIMARY KEY (nftaddr);


--
-- Name: nftarticle nftarticle_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.nftarticle
    ADD CONSTRAINT nftarticle_pkey PRIMARY KEY (id);


--
-- Name: nftcreated nftcreated_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.nftcreated
    ADD CONSTRAINT nftcreated_pkey PRIMARY KEY (id);


--
-- Name: collectioninfo nftinfo_copy_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.collectioninfo
    ADD CONSTRAINT nftinfo_copy_pkey PRIMARY KEY (id);


--
-- Name: nftinfo nftinfo_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.nftinfo
    ADD CONSTRAINT nftinfo_pkey PRIMARY KEY (id);


--
-- Name: royaltycollected royaltycollected_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.royaltycollected
    ADD CONSTRAINT royaltycollected_pkey PRIMARY KEY (id);


--
-- Name: userinfo userinfo_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.userinfo
    ADD CONSTRAINT userinfo_pkey PRIMARY KEY (account);


--
-- PostgreSQL database dump complete
--

