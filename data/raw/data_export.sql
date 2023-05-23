SELECT
    [HealthcareService].[identifier_value] AS HCS_ID
       ,[Appointment].[identifier_value] AS APP_ID
       ,CONVERT(VARCHAR(64), HASHBYTES('SHA2_256', CONCAT([Appointment].[participant_actor_Patient_value], 'noshow')), 2) AS pseudo_id
       ,[HealthcareService].[name]
       ,[HealthcareService].[partOf_HealthcareService_value]
       ,[HealthcareService].[location1_Location_value]
       ,[HealthcareService].[specialty_code]
       ,[HealthcareService].[specialty_display]
       ,[Appointment].[appointmentType_code]
       ,[Appointment].[appointmentType_display]
       ,[Poliklinisch_Consult].[soort_consult]
       ,[Appointment].[start]
       ,[Appointment].[end]
       ,[Poliklinisch_Consult].[gearriveerd]
       ,[Appointment].[created]
       ,[Appointment].[minutesDuration]
       ,[Appointment].[status]
       ,[Appointment].[status_code_original]
       ,[Appointment].[cancelationReason_code]
       ,[Appointment].[cancelationReason_display]
       ,[Poliklinisch_Consult].[verwijzer_zorgverlenerrol_identifier_value]
       ,YEAR([Patient].[birthDate]) as BIRTH_YEAR
       ,address_postalCodeNumbersNL
FROM [DWH].[models].[HealthcareService] JOIN [DWH].[models].[Appointment] ON Appointment.participant_actor_HealthcareService_value = HealthcareService.identifier_value
    JOIN [DWH].[models].Poliklinisch_Consult ON Appointment.identifier_value = Poliklinisch_Consult.afspraak_identifier_value
    JOIN [DWH].[models].Patient ON [Appointment].[participant_actor_Patient_value] = Patient.identifier_value
    JOIN [DWH].[models].[Patient_Address] ON [Patient].[identifier_value] = [Patient_Address].[parent_identifier_value] 
        AND [Appointment].[created] BETWEEN [Patient_Address].[address_period_start] AND [Patient_Address].[address_period_end]
WHERE 1 = 1
    AND HealthcareService.specialty_code in (
        'KAP', -- Kinderen
        'REV', -- Revalidatie
        'SPO', -- Sport
        'LON' -- Longen
    )
    AND afspraak_zonder_patient <> 1
    AND [Appointment].[created] >= CONVERT(DATE, '2015-01-01')
    AND [Appointment].[status] <> 'booked'