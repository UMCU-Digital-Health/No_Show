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
SELECT C.identifier_value AS APP_ID
    ,CONVERT(VARCHAR(64), HASHBYTES('SHA2_256', CONCAT(F.identifier_value, 'noshow')), 2) AS pseudo_id
    ,B.[name] AS hoofdagenda
    ,A.specialty_code
    ,D.type1_display AS soort_consult
    ,D.type1_code
    ,C.[start]
    ,C.[end]
    ,D.[statusHistory2_period_start] AS gearriveerd
    ,C.[created]
    ,C.[minutesDuration]
    ,C.[status]
    ,C.[status_code_original]
    ,C.[cancelationReason_code]
    ,C.[cancelationReason_display]
    ,YEAR(F.[birthDate]) as BIRTH_YEAR
    ,G.[address_postalCodeNumbersNL]
    ,E.[name]
    ,E.[description]
    ,F.[name_text]
    ,F.[name_given1_callMe]
    ,F.[telecom1_value]
    ,F.[telecom2_value]
    ,F.[telecom3_value]
    ,F.[birthDate]
FROM [PUB].[no_show].[HealthcareService] A JOIN [PUB].[no_show].[HealthcareService] B 
        ON A.partOf_HealthcareService_value = B.identifier_value AND A.partOf_HealthcareService_system = B.identifier_system
    JOIN [PUB].[no_show].[Appointment] C 
        ON C.participant_actor_HealthcareService_value = A.identifier_value AND C.participant_actor_HealthcareService_system = A.identifier_system
    JOIN [PUB].[no_show].Encounter D 
        ON D.appointment_Appointment_system = C.identifier_system AND D.appointment_Appointment_value = C.identifier_value
    JOIN [PUB].[no_show].Location E 
        ON D.location_Location_system = E.identifier_system AND D.location_Location_value = E.identifier_value
    JOIN [PUB].[no_show].[Patient] F 
        ON C.[participant_actor_Patient_value] = F.identifier_value
    LEFT JOIN [PUB].[no_show].[Patient_Address] G 
        ON G.[parent_identifier_value] = F.identifier_value 
WHERE 1=1
    AND A.active = 1
    AND A.identifier_value NOT IN (
        '025224',  -- Behandelaar CMH
        '028512',  -- Lab longziekten
        'S00837'   -- Sylvia Toth centrum
    )
    AND B.identifier_system = 'https://metadata.umcutrecht.nl/ids/HixAgenda'
    AND B.active = 1
    AND B.identifier_value IN (
        'A00014', 'A00030', 'A00035', 'A00036',  -- Poli Rood
        'A00006',  -- Longziekten
        'A20150')  -- Revalidatie en sport
    AND C.identifier_system = 'https://metadata.umcutrecht.nl/ids/HixAgendaAfspraak'
    AND C.[created] >= '2015-01-01'
    AND C.[start] <= @end_date
    AND D.identifier_system = 'https://metadata.umcutrecht.nl/ids/HixAgendaAfspraak'
    AND D.type2_code NOT IN ('T', 'S', 'M')
    AND D.type1_code NOT LIKE 'STS%'
    AND D.type1_code NOT LIKE 'TC%'
    AND D.without_patient <> 1
    AND E.identifier_system = 'https://metadata.umcutrecht.nl/ids/HixLocatie'
    AND E.identifier_value NOT IN (
        '0000010175', -- Dutch Scoliosis Center in Zeist
        '0000006340')  -- afdeling longziekten / B3
    AND G.address_active = 1
    AND C.participant_actor_Patient_value IN (
        SELECT J.participant_actor_Patient_value
        FROM [PUB].[no_show].[HealthcareService] H JOIN [PUB].[no_show].[HealthcareService] I 
                ON H.partOf_HealthcareService_value = I.identifier_value AND H.partOf_HealthcareService_system = I.identifier_system
            JOIN [PUB].[no_show].[Appointment] J 
                ON J.participant_actor_HealthcareService_value = H.identifier_value AND J.participant_actor_HealthcareService_system = H.identifier_system
            JOIN [PUB].[no_show].Encounter K 
                ON K.appointment_Appointment_system = J.identifier_system AND K.appointment_Appointment_value = J.identifier_value
            JOIN [PUB].[no_show].Location L 
                ON K.location_Location_system = L.identifier_system AND K.location_Location_value = L.identifier_value
        WHERE 1=1
            AND H.active = 1
            AND H.identifier_value NOT IN (
                '025224',  -- Behandelaar CMH
                '028512',  -- Lab longziekten
                'S00837'   -- Sylvia Toth centrum
            )
            AND I.identifier_system = 'https://metadata.umcutrecht.nl/ids/HixAgenda'
            AND I.active = 1
            AND I.identifier_value IN (
                'A00014', 'A00030', 'A00035', 'A00036',  -- Poli Rood
                'A00006',  -- Longziekten
                'A20150')  -- Revalidatie en sport
            AND J.identifier_system = 'https://metadata.umcutrecht.nl/ids/HixAgendaAfspraak'
            AND CONVERT(DATE, J.[start]) = @start_date
            AND J.[status] = 'booked'
            AND K.identifier_system = 'https://metadata.umcutrecht.nl/ids/HixAgendaAfspraak'
            AND K.type2_code NOT IN ('T', 'S', 'M')
            AND K.type1_code NOT LIKE 'STS%'
            AND K.type1_code NOT LIKE 'TC%'
            AND K.without_patient <> 1
            AND L.identifier_system = 'https://metadata.umcutrecht.nl/ids/HixLocatie'
            AND L.identifier_value NOT IN (
                '0000010175', -- Dutch Scoliosis Center in Zeist
                '0000006340')  -- afdeling longziekten / B3
    )
    ORDER BY pseudo_id, C.start;
