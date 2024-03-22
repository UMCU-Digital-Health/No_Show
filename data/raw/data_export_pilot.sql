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
    AND A.identifier_system = 'https://metadata.umcutrecht.nl/ids/HixSubAgenda'
    AND A.identifier_value NOT IN (
        'Z10351', 'Z10330', 'Z10307', 'Z10362', 'Z10438',  -- Hartgroepen 1 t/m 5 (REV)
        'Z10455',  -- Behandelaar CMH
        'ZH0302', 'Z01613', 'Z01577'  -- LAB Longziekten
    )
    AND B.identifier_system = 'https://metadata.umcutrecht.nl/ids/HixAgenda'
    AND B.active = 1
    AND B.identifier_value IN (
        'ZH0307',  -- RF&S Revalidatiegeneeskunde
        'ZH0435',  -- RF&S Sportgeneeskunde
        'ZH0183',  -- Longziekten
        'ZH0153',  -- Kind-KNO
        'ZH0159',  -- Kind-Neurologie
        'ZH0163',  -- Kind-Orthopedie
        'ZH0165'   -- Kind-Plastische chirurgie
    )  
    AND C.identifier_system = 'https://metadata.umcutrecht.nl/ids/HixAgendaAfspraak'
    AND CONVERT(DATE, C.start) >= '2015-01-01'
    AND CONVERT(DATE, C.start) <= '2023-11-01'
    AND C.status <> 'booked'
    AND D.identifier_system = 'https://metadata.umcutrecht.nl/ids/HixAgendaAfspraak'
    AND D.type2_code NOT IN ('T', 'S', 'M')
    AND D.type1_display NOT LIKE '%telefo%'
    AND D.type1_display NOT LIKE 'TC%'
    AND D.without_patient <> 1
    AND E.identifier_system = 'https://metadata.umcutrecht.nl/ids/HixLocatie'
    AND E.identifier_value NOT IN (
        'ZH00000698', -- Dutch Scoliosis Center in Zeist
        'ZH00000407')  -- afdeling longziekten / B3
    AND G.address_active = 1
ORDER BY B.name, A.name, C.start
