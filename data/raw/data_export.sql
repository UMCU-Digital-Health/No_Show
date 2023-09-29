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
FROM [DWH].[models].[HealthcareService] A JOIN [DWH].[models].[HealthcareService] B 
        ON A.partOf_HealthcareService_value = B.identifier_value AND A.partOf_HealthcareService_system = B.identifier_system
    JOIN [DWH].[models].[Appointment] C 
        ON C.participant_actor_HealthcareService_value = A.identifier_value AND C.participant_actor_HealthcareService_system = A.identifier_system
    JOIN [DWH].[models].Encounter D 
        ON D.appointment_Appointment_system = C.identifier_system AND D.appointment_Appointment_value = C.identifier_value
    JOIN [DWH].[models].Location E 
        ON D.location_Location_system = E.identifier_system AND D.location_Location_value = E.identifier_value
    JOIN [DWH].[models].[Patient] F 
        ON C.[participant_actor_Patient_value] = F.identifier_value
    LEFT JOIN [DWH].[models].[Patient_Address] G 
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
    AND C.created >= '2015-01-01'
    AND C.created <= '2023-05-16'
    AND C.status <> 'booked'
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
ORDER BY B.name, A.name, C.start
