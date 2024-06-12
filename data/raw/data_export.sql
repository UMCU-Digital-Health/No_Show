SELECT APP.identifier_value AS APP_ID
    ,CONVERT(VARCHAR(64), HASHBYTES('SHA2_256', CONCAT(PAT.identifier_value, 'noshow')), 2) AS pseudo_id
    ,HOOFDAGENDA.[name] AS hoofdagenda
    ,SUBAGENDA.specialty_code
    ,SUBAGENDA.name 
    ,ENC.type1_display AS soort_consult
    ,ENC.type1_code
    ,APP.[start]
    ,APP.[end]
    ,ENC.[statusHistory2_period_start] AS gearriveerd
    ,APP.[created]
    ,APP.[minutesDuration]
    ,APP.[status]
    ,APP.[status_code_original]
    ,APP.[cancelationReason_code]
    ,APP.[cancelationReason_display]
    ,YEAR(PAT.[birthDate]) as BIRTH_YEAR
    ,ADDR.[address_postalCodeNumbersNL]
    ,LOC.[name]
    ,LOC.[description]
FROM [DWH].[models].[HealthcareService] SUBAGENDA JOIN [DWH].[models].[HealthcareService] HOOFDAGENDA
        ON SUBAGENDA.partOf_HealthcareService_value = HOOFDAGENDA.identifier_value AND SUBAGENDA.partOf_HealthcareService_system = HOOFDAGENDA.identifier_system
    JOIN [DWH].[models].[Appointment] APP 
        ON APP.participant_actor_HealthcareService_value = SUBAGENDA.identifier_value AND APP.participant_actor_HealthcareService_system = SUBAGENDA.identifier_system
    JOIN [DWH].[models].Encounter ENC
        ON ENC.appointment_Appointment_system = APP.identifier_system AND ENC.appointment_Appointment_value = APP.identifier_value
    LEFT JOIN [DWH].[models].Location LOC
        ON ENC.location_Location_system = LOC.identifier_system AND ENC.location_Location_value = LOC.identifier_value
    JOIN [DWH].[models].[Patient] PAT
        ON APP.[participant_actor_Patient_value] = PAT.identifier_value
    LEFT JOIN [DWH].[models].[Patient_Address] ADDR
        ON ADDR.[parent_identifier_value] = PAT.identifier_value 
WHERE 1=1
    AND SUBAGENDA.active = 1
    AND SUBAGENDA.identifier_system = 'https://metadata.umcutrecht.nl/ids/HixSubAgenda'
    AND SUBAGENDA.identifier_value NOT IN (
        'Z10351', 'Z10330', 'Z10307', 'Z10362', 'Z10438',  -- Hartgroepen 1 t/m 5 (REV)
        'Z10455',  -- Behandelaar CMH
        'ZH0302', 'Z01613', 'Z01577',  -- LAB Longziekten
        'Z06676', -- Ciliopathie
        'Z07053', -- PMC
        'Z07081', -- Research DER
        'Z07078', -- Bioday kind
        'Z04778', -- afgifteloket van het lab.
        'Z04755' -- afgifteloket van het laboratorium
    )
    AND HOOFDAGENDA.identifier_system = 'https://metadata.umcutrecht.nl/ids/HixAgenda'
    AND HOOFDAGENDA.active = 1
    AND (
        HOOFDAGENDA.identifier_value IN (
            -- Revalidatie en sport
            'ZH0307',  -- RF&S Revalidatiegeneeskunde
            'ZH0435',  -- RF&S Sportgeneeskunde
            'ZH0444',  -- RF&S Psychologie
            'ZH0091',  -- RF&S Dietetiek
            'ZH0437',  -- RF&S Ergotherapie
            'ZH0436',  -- RF&S Fysiotherapie
            'ZH0439',  -- RF&S Maatschappelijk werk
            'ZH0438',  -- RF&S Logopedie
            'ZH0436',   -- RF&S Fysiotherapie
            -- Poli blauw
            'ZH0156', -- Kind-Nefrologie 
            'ZH0139', -- Kind-Endocrinologie
            'ZH0138', -- Kind-Dermatologie 
            'ZH0129',  -- Kind-Algemene Pediatrie
            -- Longziekten
            'ZH0183',  -- Longziekten
            'ZH0034'  -- Centrum voor Thuisbeademing
        )  OR 
        (HOOFDAGENDA.identifier_value = 'ZH0152' AND SUBAGENDA.identifier_value = 'Z00936') -- CTB spreekuur kind klz
        ) 
    AND APP.identifier_system = 'https://metadata.umcutrecht.nl/ids/HixAgendaAfspraak'
    AND APP.created >= '2015-01-01'
    AND APP.created <= '2024-05-31'
    AND APP.status <> 'booked'
    AND ENC.identifier_system = 'https://metadata.umcutrecht.nl/ids/HixAgendaAfspraak'
    AND ENC.type2_code NOT IN ('T', 'S', 'M')
    AND ENC.type1_display NOT LIKE '%telefo%'
    AND ENC.type1_display NOT LIKE 'TC%'
    AND ENC.without_patient <> 1
    AND ADDR.address_active = 1
ORDER BY HOOFDAGENDA.name, SUBAGENDA.name, APP.start
