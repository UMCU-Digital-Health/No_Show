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
    ,HOOFDAGENDA.[identifier_value] AS hoofdagenda_id
    ,SUBAGENDA.[identifier_value] AS subagenda_id
    ,SUBAGENDA.specialty_code
    ,ENC.type1_display AS soort_consult
    ,ENC.type1_code AS afspraak_code
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
    ,PAT.identifier_value as patient_id
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
    AND HOOFDAGENDA.identifier_system = 'https://metadata.umcutrecht.nl/ids/HixAgenda'
    AND HOOFDAGENDA.active = 1
    AND HOOFDAGENDA.identifier_value IN (
        -- Revalidatie en sport
        'ZH0307',  -- RF&S Revalidatiegeneeskunde
        'ZH0435',  -- RF&S Sportgeneeskunde
        -- Poli blauw
        'ZH0156', -- Kind-Nefrologie 
        'ZH0139', -- Kind-Endocrinologie
        'ZH0138', -- Kind-Dermatologie 
        'ZH0129', -- Kind-Algemene Pediatrie
        'ZH0152', -- Kind-KLZ
        'ZH0130', -- Kind-Allergologie
        'ZH0150', -- Kind-Immunologie
        'ZH0149', -- Kind-Hematologie
        'ZH0154', -- Kind-MDL
        'ZH0171', -- Kind-Urologie
        -- Poli rood
        'ZH0153', -- Kind-KNO
        'ZH0133', -- Kind-Bijzondere tandheelkunde
        'ZH0151', -- Kind-Kaakchirurgie
        'ZH0162', -- Kind-Orthodontie
        'ZH0165', -- Kind-Plastische chirurgie
        'ZH0159', -- Kind-Neurologie
        'ZH0158', -- Kind-Neurochirurgie
        'ZH0148', -- Kind-Gynaecologie
        'ZH0155', -- Kind-Metabole ziekten
        'ZH0135', -- Kind-Chirurgie
        'ZH0163', -- Kind-Orthopedie
        'ZH0169', -- Kind-Revalidatie
        'ZH0157', -- Kind-Neonatologie
        'ZH0164', -- Kind-Pijnbehandeling
        'ZH0131', -- Kind-Anesthesiologie
        -- Kind Cardiologie
        'ZH0134',
        -- Longziekten
        'ZH0183',  -- Longziekten
        'ZH0034',  -- Centrum voor Thuisbeademing
        -- Cardiologie
        'ZH0017',  -- cardiologie
        -- Neurologie
        'ZH0318',  -- Spieren voor Spieren kinderen
        -- Benigne Hematologie
        'ZH0410', -- Van creveldkliniek
        --Dermatologie
        'ZH0087', 
        -- Allergologie
        'ZH0007',
        -- Reumatologie
        'ZH0305',
        -- MDL
        'ZH0184',
        -- Nefrologie
        'ZH0193',
        -- Geriatrie
        'ZH0111',
        -- Interne geneeskunde
        'ZH0123', -- Interne geneeskunde
        'ZH0122', -- Infectieziekten
        'ZH0088', -- Diabetologie
        'ZH0096', -- Endocrinologie
        'ZH0413' -- Vasculaire geneeskunde
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
        WHERE 1=1
            AND SUBAGENDA2.active = 1
            AND SUBAGENDA2.identifier_system = 'https://metadata.umcutrecht.nl/ids/HixSubAgenda'
            AND HOOFDAGENDA2.identifier_system = 'https://metadata.umcutrecht.nl/ids/HixAgenda'
            AND HOOFDAGENDA2.active = 1
            AND HOOFDAGENDA2.identifier_value IN (
                -- Revalidatie en sport
                'ZH0307',  -- RF&S Revalidatiegeneeskunde
                'ZH0435',  -- RF&S Sportgeneeskunde
                -- Poli blauw
                'ZH0156', -- Kind-Nefrologie 
                'ZH0139', -- Kind-Endocrinologie
                'ZH0138', -- Kind-Dermatologie 
                'ZH0129', -- Kind-Algemene Pediatrie
                'ZH0152', -- Kind-KLZ
                'ZH0130', -- Kind-Allergologie
                'ZH0150', -- Kind-Immunologie
                'ZH0149', -- Kind-Hematologie
                'ZH0154', -- Kind-MDL
                'ZH0171', -- Kind-Urologie
                -- Poli rood
                'ZH0153', -- Kind-KNO
                'ZH0133', -- Kind-Bijzondere tandheelkunde
                'ZH0151', -- Kind-Kaakchirurgie
                'ZH0162', -- Kind-Orthodontie
                'ZH0165', -- Kind-Plastische chirurgie
                'ZH0159', -- Kind-Neurologie
                'ZH0158', -- Kind-Neurochirurgie
                'ZH0148', -- Kind-Gynaecologie
                'ZH0155', -- Kind-Metabole ziekten
                'ZH0135', -- Kind-Chirurgie
                'ZH0163', -- Kind-Orthopedie
                'ZH0169', -- Kind-Revalidatie
                'ZH0157', -- Kind-Neonatologie
                'ZH0164', -- Kind-Pijnbehandeling
                'ZH0131', -- Kind-Anesthesiologie
                -- Kind Cardiologie
                'ZH0134',
                -- Longziekten
                'ZH0183',  -- Longziekten
                'ZH0034',  -- Centrum voor Thuisbeademing
                -- Cardiologie
                'ZH0017',  -- cardiologie
                -- Neurologie
                'ZH0318',  -- Spieren voor Spieren kinderen
                -- Benigne Hematologie
                'ZH0410', -- Van creveldkliniek
                --Dermatologie
                'ZH0087', 
                -- Allergologie
                'ZH0007',
                -- Reumatologie
                'ZH0305',
                -- MDL
                'ZH0184',
                -- Nefrologie
                'ZH0193',
                -- Geriatrie
                'ZH0111',
                -- Interne geneeskunde
                'ZH0123', -- Interne geneeskunde
                'ZH0122', -- Infectieziekten
                'ZH0088', -- Diabetologie
                'ZH0096', -- Endocrinologie
                'ZH0413' -- Vasculaire geneeskunde
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