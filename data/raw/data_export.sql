SELECT
    [HealthcareService].[identifier_value] AS HCS_ID
       ,[Appointment].[identifier_value] AS APP_ID
       ,CONVERT(VARCHAR(64), HASHBYTES('SHA2_256', CONCAT([Appointment].[participant_actor_Patient_value], 'noshow')), 2) AS pseudo_id
       ,[HealthcareService].[specialty_code]
       ,[HealthcareService].[specialty_display]
       ,[Poliklinisch].[soort_consult]
       ,[Poliklinisch].[poli_ident]
       ,[Appointment].[start]
       ,[Appointment].[end]
       ,[Poliklinisch].[gearriveerd]
       ,[Appointment].[created]
       ,[Appointment].[minutesDuration]
       ,[Appointment].[status]
       ,[Appointment].[status_code_original]
       ,[Appointment].[cancelationReason_code]
       ,[Appointment].[cancelationReason_display]
       ,YEAR([Patient].[birthDate]) as BIRTH_YEAR
       ,address_postalCodeNumbersNL
       ,Location.name
       ,Location.[description]
FROM [DWH].[models].[HealthcareService] JOIN [DWH].[models].[Appointment] ON Appointment.participant_actor_HealthcareService_value = HealthcareService.identifier_value
    JOIN (
        SELECT pc.afspraak_identifier_value, pc.polibalie_locatie_identifier_system, pc.polibalie_locatie_identifier_value, pc.soort_consult, pc.gearriveerd, pc.afspraak_zonder_patient, 'Consult' as poli_ident
        FROM [DWH].[models].Poliklinisch_Consult pc
        UNION
        SELECT pv.afspraak_identifier_value, pv.polibalie_locatie_identifier_system, pv.polibalie_locatie_identifier_value, pv.soort_consult, pv.gearriveerd, pv.afspraak_zonder_patient, 'Verrichting' as poli_ident
        FROM [DWH].[models].Poliklinisch_Verrichting pv
    ) Poliklinisch
    ON Appointment.identifier_value = Poliklinisch.afspraak_identifier_value
    JOIN [DWH].[models].Patient ON [Appointment].[participant_actor_Patient_value] = Patient.identifier_value
    JOIN [DWH].[models].[Patient_Address] ON [Patient].[identifier_value] = [Patient_Address].[parent_identifier_value] 
        AND [Appointment].[created] BETWEEN [Patient_Address].[address_period_start] AND [Patient_Address].[address_period_end]
    LEFT JOIN DWH.models.Location ON Poliklinisch.polibalie_locatie_identifier_system = [Location].identifier_system AND Poliklinisch.[polibalie_locatie_identifier_value] = Location.identifier_value
WHERE 1 = 1
    AND afspraak_zonder_patient <> 1
    AND [Appointment].[created] >= CONVERT(DATE, '2015-01-01')
    AND [Appointment].[created] <= CONVERT(DATE, '2023-05-16')
    AND [Appointment].[status] <> 'booked'
    AND [Location].[name] IN (
        'UG', 'AAV', 'AZ', 'BN', 'BF', 'ABG', 'BE', 'BO',  'EG', 'BG', --afdeling longziekten
        'MA', 'MB', -- Sport & revalidatie
        'WQ', 'WY', 'WV', 'WW', 'WL', 'W12', 'WS', 'K1', 'K5', 'W1', 'WP', 'W2', 'KW', 'WM', 'W#', 'W*', 'WR', 'W4' --WKZ
    )
    AND [soort_consult] NOT IN ('Telefonisch', 'Screen to screen', 'E-Mail')
