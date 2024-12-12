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
    ,ENC.[arrival] AS gearriveerd
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
            'ZH0413', -- Vasculaire geneeskunde
            -- Longfunctie
            'ZH0182',
            -- Neurologie & neurochiurgie
            'ZH0005', -- Algemene neurochirurgie
            'ZH0006', -- Algemene neurologie
            'ZH0035', -- Cerebrovasculaire ziekten
            'ZH0194', -- Neuro oncologie
            -- Neuromusculaire ziekten
            'ZH0197', -- Neuromusculaire ziekten
            'ZH0105', -- Functionele neurochirurgie
            -- Zorglijn affectieve en psychotische stoornissen
            'ZH0298', -- PSY stemming en psychose
            -- Zorglijn Diagnostiek en vroege psychose
            'ZH0299', -- PSY Diagnostiek en vroege psychose
            -- Zorglijn Ontwikkeling in perspectief
            'ZH0300', -- PSY Ontwikkeling in perspectief
            -- Zorglijn Acute en intensieve zorg
            'ZH0297', -- PSY Acute en intensieve zorg
            -- Oncologische urologie
            'ZH0033', -- B&O Urologische oncologie
            -- Hartfunctie
            'ZH0116', -- Functie Hart
            -- Medische oncoloie
            'ZH0028', -- B&O Medische oncologie
            -- Hematologie
            'ZH0025', -- B&O Hematologie
            -- Gynaecologische oncologie
            'ZH0024', -- B&O Gynaecologische oncologie
            -- Chirurgische oncologie
            'ZH0020', -- B&O Chirurgische oncologie
            -- Hoofd Hals oncologie
            'ZH0027', -- B&O KNH oncologie
            -- Functie KNF
            'ZH0175', -- Functie KNF
            -- Orthopedie
            'ZH0210', -- Orthopedie
            -- Urologie
            'ZH0324', -- Urologie
            -- Plastische chirurgie
            'ZH0213', -- Plastische Chirurgie
            -- Traumatologie Heelkunde
            'ZH0343', -- Traumatologie
            'ZH0117', -- Heelkunde
            -- Vaatchirurgie
            'ZH0401', -- Vaatcentrum
            -- KNO
            'ZH0178', -- KNO
            -- Functiecentrum KNO
            'ZH0104', -- Functiecentrum KNO
            -- MKA
            'ZH0026', -- B&O Kaakchirurgie en oncologie
            'ZH0191', -- Mondziekten / kaakchirugie
            -- Bijzondere tandheelkunde
            'ZH0002', -- A&G
            'ZH0014', -- Bijzondere tandheelkunde
            -- Oogheelkunde
            'ZH0208', -- Oogheelkunde
            'CS0140', -- Functie oogheelkunde
            -- Anesthesiologie
            'ZH0010', -- Anesthesiologie
            -- Pijncentrum
            'ZH0211', -- Pijnbehandeling
            -- Genetica
            'ZH0110', -- Genetica
            'ZH0160', -- Kind-ontwikkelingsachterstand
            -- Prikpoli
            '020434', -- Kind-laboratorium
            'ZH0414', -- VAS-teamagenda            
            -- Fertiliteit & gyneacologie
            'ZH04222' -- Voortplanting & gynaecologie
        )
    AND APP.identifier_system = 'https://metadata.umcutrecht.nl/ids/HixAgendaAfspraak'
    AND APP.created >= '2016-01-01'
    AND APP.created <= '2024-11-01'
    AND APP.status <> 'booked'
    AND ENC.identifier_system = 'https://metadata.umcutrecht.nl/ids/HixAgendaAfspraak'
    AND ENC.type2_code NOT IN ('T', 'S', 'M')
    AND ENC.type1_display NOT LIKE '%telefo%'
    AND ENC.type1_display NOT LIKE 'TC%'
    AND ENC.without_patient <> 1
    AND ADDR.address_active = 1
ORDER BY HOOFDAGENDA.name, SUBAGENDA.name, APP.start
