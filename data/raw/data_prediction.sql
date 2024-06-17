DECLARE @start_date DATE = GETDATE();
DECLARE @end_date DATE = DATEADD(DAY, 14, @start_date);
DECLARE @num_days INT = 3;

-- Calculate the date in 3 working days (excluding weekends)
WHILE @num_days > 0
BEGIN
    SET @start_date = DATEADD(DAY, 1, @start_date);
    IF DATEPART(WEEKDAY, @start_date) NOT IN (1, 7)
    BEGIN
        SET @num_days = @num_days - 1;
    END
END

-- Main Query
SELECT APP.identifier_value AS APP_ID
    ,CONVERT(VARCHAR(64), HASHBYTES('SHA2_256', CONCAT(PAT.identifier_value, 'noshow')), 2) AS pseudo_id
    ,HOOFDAGENDA.[name] AS hoofdagenda
    ,SUBAGENDA.specialty_code
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
    ,PAT.[name_text]
    ,PAT.[name_given1_callMe]
    ,PAT.[telecom1_value]
    ,PAT.[telecom2_value]
    ,PAT.[telecom3_value]
    ,PAT.[birthDate]
FROM [PUB].[no_show].[HealthcareService] SUBAGENDA JOIN [PUB].[no_show].[HealthcareService] HOOFDAGENDA 
        ON SUBAGENDA.partOf_HealthcareService_value = HOOFDAGENDA.identifier_value AND SUBAGENDA.partOf_HealthcareService_system = HOOFDAGENDA.identifier_system
    JOIN [PUB].[no_show].[Appointment] APP 
        ON APP.participant_actor_HealthcareService_value = SUBAGENDA.identifier_value AND APP.participant_actor_HealthcareService_system = SUBAGENDA.identifier_system
    JOIN [PUB].[no_show].Encounter ENC 
        ON ENC.appointment_Appointment_system = APP.identifier_system AND ENC.appointment_Appointment_value = APP.identifier_value
    LEFT JOIN [PUB].[no_show].Location LOC
        ON ENC.location_Location_system = LOC.identifier_system AND ENC.location_Location_value = LOC.identifier_value
    JOIN [PUB].[no_show].[Patient] PAT
        ON APP.[participant_actor_Patient_value] = PAT.identifier_value
    LEFT JOIN [PUB].[no_show].[Patient_Address] ADDR
        ON ADDR.[parent_identifier_value] = PAT.identifier_value 
WHERE 1=1
    AND SUBAGENDA.active = 1
    AND SUBAGENDA.identifier_system = 'https://metadata.umcutrecht.nl/ids/HixSubAgenda'
    AND SUBAGENDA.identifier_value NOT IN (
        'Z10351', 'Z10330', 'Z10307', 'Z10362', 'Z10438',  -- Hartgroepen 1 t/m 5 (REV)
        'ZH0082', 'ZH0085', 'ZH0086', 'ZH0087', 'ZH0088',  -- Hartgroepen 1 t/m 5 (FYS)
        'Z10455',  -- Behandelaar CMH
        'ZH0302', 'Z01613', 'Z01577',  -- LAB Longziekten
        -- Huisbezoeken van Centrum voor Thuisbeademing
        'Z04789', 'Z04792', 'Z04790', 'Z04791', 'Z04764', 'Z04765', 'Z04760', 
        'Z04766', 'Z04757', '029756', 'Z04745', 'Z04763', 'ZH0633', 'Z04761',
        'Z04787', 'Z04747', 'Z04767', 'Z04746', 'Z04769', 'Z04758', 'Z04788',
        'Z04786', 'Z04759',
        --
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
            -- 'ZH0307',  -- RF&S Revalidatiegeneeskunde
            -- 'ZH0435',  -- RF&S Sportgeneeskunde
            -- 'ZH0444',  -- RF&S Psychologie
            -- 'ZH0091',  -- RF&S Dietetiek
            -- 'ZH0437',  -- RF&S Ergotherapie
            -- 'ZH0436',  -- RF&S Fysiotherapie
            -- 'ZH0439',  -- RF&S Maatschappelijk werk
            -- 'ZH0438',  -- RF&S Logopedie
            -- 'ZH0436',   -- RF&S Fysiotherapie
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
    AND APP.[created] >= '2015-01-01'
    AND APP.[start] <= @end_date
    AND ENC.identifier_system = 'https://metadata.umcutrecht.nl/ids/HixAgendaAfspraak'
    AND ENC.type2_code NOT IN ('T', 'S', 'M')
    AND ENC.type1_display NOT LIKE '%telefo%'
    AND ENC.type1_display NOT LIKE 'TC%'
    AND ENC.without_patient <> 1
    AND ADDR.address_active = 1
    AND APP.participant_actor_Patient_value IN (
        SELECT APP2.participant_actor_Patient_value
        FROM [PUB].[no_show].[HealthcareService] SUBAGENDA2 JOIN [PUB].[no_show].[HealthcareService] HOOFDAGENDA2
                ON SUBAGENDA2.partOf_HealthcareService_value = HOOFDAGENDA2.identifier_value AND SUBAGENDA2.partOf_HealthcareService_system = HOOFDAGENDA2.identifier_system
            JOIN [PUB].[no_show].[Appointment] APP2 
                ON APP2.participant_actor_HealthcareService_value = SUBAGENDA2.identifier_value AND APP2.participant_actor_HealthcareService_system = SUBAGENDA2.identifier_system
            JOIN [PUB].[no_show].Encounter ENC2
                ON ENC2.appointment_Appointment_system = APP2.identifier_system AND ENC2.appointment_Appointment_value = APP2.identifier_value
            LEFT JOIN [PUB].[no_show].Location LOC2 
                ON ENC2.location_Location_system = LOC2.identifier_system AND ENC2.location_Location_value = LOC2.identifier_value
        WHERE 1=1
            AND SUBAGENDA2.active = 1
            AND SUBAGENDA2.identifier_system = 'https://metadata.umcutrecht.nl/ids/HixSubAgenda'
            AND SUBAGENDA2.identifier_value NOT IN (
                'Z10351', 'Z10330', 'Z10307', 'Z10362', 'Z10438',  -- Hartgroepen 1 t/m 5 (REV)
                'ZH0082', 'ZH0085', 'ZH0086', 'ZH0087', 'ZH0088',  -- Hartgroepen 1 t/m 5 (FYS)
                'Z10455',  -- Behandelaar CMH
                'ZH0302', 'Z01613', 'Z01577',  -- LAB Longziekten
                 -- Huisbezoeken van Centrum voor Thuisbeademing
                'Z04789', 'Z04792', 'Z04790', 'Z04791', 'Z04764', 'Z04765', 'Z04760', 
                'Z04766', 'Z04757', '029756', 'Z04745', 'Z04763', 'ZH0633', 'Z04761',
                'Z04787', 'Z04747', 'Z04767', 'Z04746', 'Z04769', 'Z04758', 'Z04788',
                'Z04786', 'Z04759',
                --
                'Z06676', -- Ciliopathie
                'Z07053', -- PMC
                'Z07081', -- Research DER
                'Z07078', -- Bioday kind
                'Z04778', -- afgifteloket van het lab.
                'Z04755' -- afgifteloket van het laboratorium
            )
            AND HOOFDAGENDA2.identifier_system = 'https://metadata.umcutrecht.nl/ids/HixAgenda'
            AND HOOFDAGENDA2.active = 1
            AND (
                HOOFDAGENDA2.identifier_value IN (
                    -- Revalidatie en sport
                    -- 'ZH0307',  -- RF&S Revalidatiegeneeskunde
                    -- 'ZH0435',  -- RF&S Sportgeneeskunde
                    -- 'ZH0444',  -- RF&S Psychologie
                    -- 'ZH0091',  -- RF&S Dietetiek
                    -- 'ZH0437',  -- RF&S Ergotherapie
                    -- 'ZH0436',  -- RF&S Fysiotherapie
                    -- 'ZH0439',  -- RF&S Maatschappelijk werk
                    -- 'ZH0438',  -- RF&S Logopedie
                    -- 'ZH0436',   -- RF&S Fysiotherapie
                    -- Poli blauw
                    'ZH0156', -- Kind-Nefrologie 
                    'ZH0139', -- Kind-Endocrinologie
                    'ZH0138', -- Kind-Dermatologie 
                    'ZH0129',  -- Kind-Algemene Pediatrie
                    -- Longziekten
                    'ZH0183',  -- Longziekten
                    'ZH0034'  -- Centrum voor Thuisbeademing
                )  OR
                (HOOFDAGENDA2.identifier_value = 'ZH0152' AND SUBAGENDA2.identifier_value = 'Z00936') -- CTB spreekuur kind klz
                ) 
            AND APP2.identifier_system = 'https://metadata.umcutrecht.nl/ids/HixAgendaAfspraak'
            AND CONVERT(DATE, APP2.[start]) = @start_date
            AND APP2.[status] = 'booked'
            AND ENC2.identifier_system = 'https://metadata.umcutrecht.nl/ids/HixAgendaAfspraak'
            AND ENC2.type2_code NOT IN ('T', 'S', 'M')
            AND ENC2.type1_display NOT LIKE '%telefo%'
            AND ENC2.type1_display NOT LIKE 'TC%'
            AND ENC2.without_patient <> 1
    )
ORDER BY pseudo_id, APP.start;
