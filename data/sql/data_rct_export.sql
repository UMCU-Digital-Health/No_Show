SELECT APP.identifier_value AS APP_ID
    ,HOOFDAGENDA.[name] AS hoofdagenda
    ,SUBAGENDA.specialty_code
    ,SUBAGENDA.name 
    ,ENC.type1_display AS soort_consult
    ,ENC.type1_code AS afspraak_code
    ,APP.[start]
    ,APP.[end]
    ,APP.[status]
    ,APP.[status_code_original]
    ,APP.[cancelationReason_code]
    ,APP.[cancelationReason_display]
FROM [DWH].[models].[HealthcareService] SUBAGENDA JOIN [DWH].[models].[HealthcareService] HOOFDAGENDA
        ON SUBAGENDA.partOf_HealthcareService_value = HOOFDAGENDA.identifier_value AND SUBAGENDA.partOf_HealthcareService_system = HOOFDAGENDA.identifier_system
    JOIN [DWH].[models].[Appointment] APP 
        ON APP.participant_actor_HealthcareService_value = SUBAGENDA.identifier_value AND APP.participant_actor_HealthcareService_system = SUBAGENDA.identifier_system
    JOIN [DWH].[models].Encounter ENC
        ON ENC.appointment_Appointment_system = APP.identifier_system AND ENC.appointment_Appointment_value = APP.identifier_value
WHERE 1=1
    AND SUBAGENDA.identifier_system = 'https://metadata.umcutrecht.nl/ids/HixSubAgenda'
    AND HOOFDAGENDA.identifier_system = 'https://metadata.umcutrecht.nl/ids/HixAgenda'
    AND (
        HOOFDAGENDA.identifier_value IN (
            -- Poli blauw
            'ZH0156', -- Kind-Nefrologie 
            'ZH0139', -- Kind-Endocrinologie
            'ZH0138', -- Kind-Dermatologie 
            'ZH0129', -- Kind-Algemene Pediatrie
            -- Longziekten
            'ZH0183',  -- Longziekten
            'ZH0034',  -- Centrum voor Thuisbeademing
            -- Cardiologie
            'ZH0017'  -- cardiologie
        )  OR
        (
            HOOFDAGENDA.identifier_value IN (
                -- Revalidatie en sport
                'ZH0307',  -- RF&S Revalidatiegeneeskunde
                'ZH0435'  -- RF&S Sportgeneeskunde
            ) AND ENC.type1_code IN(
                'CF15',
                'CF30',
                'CF45',
                'CF60',
                'CFCRE',
                'CFMYDY',
                'CFNOIC',
                'CFOIMD',
                'CFOIMV',
                'CFORT',
                'CFPRB',
                'CFPRBSAB',
                'NFALS',
                'NFCVA',
                'NFCWP',
                'NFMYDY',
                'NFNAH',
                'NFNMZ',
                'NFNONC',
                'NFPRB',
                'NFREV',
                'NFREVK',
                'NFRONC',
                'NFSARC',
                'NFSD',
                'NFSPAS',
                'NFTRAUMA',
                'NFVCI',
                'NF',
                'NFSO',
                'VBSOARTS',
                'VBSOHART',
                'VBSOHINS',
                'VBSOINSP',
                'VGSO+ART',
                'VGSO+INS',
                'VGSOARTS',
                'VGSOINSP',
                'VMITCHAR',
                'VMITHARC',
                'VMITHART',
                'VMITHINS'
            )
        )
    )
    AND APP.identifier_system = 'https://metadata.umcutrecht.nl/ids/HixAgendaAfspraak'
    AND APP.start >= '2024-06-18'
    AND APP.start <= '2024-10-17'
    AND ENC.identifier_system = 'https://metadata.umcutrecht.nl/ids/HixAgendaAfspraak'
ORDER BY HOOFDAGENDA.name, SUBAGENDA.name, APP.start