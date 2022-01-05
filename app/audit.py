def assessment_flow(assessment, results):
    print(assessment, results)

    score = 0

    if assessment == 'audit-c':
        n_question = 3
        for i in range(n_question):
            if str(i) not in results:
                return 'audit-c error', -1
            score += results[str(i)]
        
        if score > 4:
            return 'audit-c high risk', score
        if score > 2:
            return 'audit-c medium risk', score
        return 'audit-c low risk', score
    
    if assessment == 'audit-10':
        n_question = 10
        for i in range(n_question):
            if str(i) not in results:
                return 'audit-10 error', score
            score += results[str(i)]
        
        if score > 14:
            return 'audit-10 >= 15'
        return 'audit-10 < 15', score
    
    return 'audit-c results', score



assessment = {
    'audit-c': {
        'en': [
            {
                'question': 'Within the past 12 months, how often did you have a drink of alcohol?', 
                'answer': [
                    ['Never', 0], 
                    ['Once per month or less', 1], 
                    ['2-4 times a month', 2], 
                    ['2-3 times a week', 3], 
                    ['4 or more times a week', 4]
                ]
            }, 
            {
                'question': 'Within the past 12 months, how many standard drinks containing alcohol did you have on a typical day?', 
                'answer': [
                    ['1 or 2', 0], 
                    ['3 or 4', 1], 
                    ['5 or 6', 2], 
                    ['7 to 9', 3], 
                    ['10 or more', 4]
                ]
            }, 
            {
                'question': 'Within the past 12 months, how often did you have six or more drinks on one occasion?', 
                'answer': [
                    ['Never', 0], 
                    ['Less than monthly', 1], 
                    ['Monthly', 2], 
                    ['Weekly', 3], 
                    ['Daily or almost daily', 4]
                ]
            }
        ], 
        'ms': [
            {
                'question': ' Dalam tempoh 12 bulan yang lepas berapa kerapkah anda minum minuman keras / arak / beralkohol?', 
                'answer': [
                    ['Tak pernah', 0], 
                    ['Sekali sebulan atau kurang', 1], 
                    ['2-4 kali sebulan', 2], 
                    ['2-3 kali seminggu', 3], 
                    ['4 kali atau lebih seminggu', 4]
                ]
            }, 
            {
                'question': ' Kebiasaannya pada hari yang anda minum, berapa banyakkah anda minum minuman keras / arak / beralkohol?', 
                'answer': [
                    ['1 atau 2 minuman alkohol', 0], 
                    ['3 atau 4 minuman alkohol', 1], 
                    ['5 atau 6 minuman alkohol', 2], 
                    ['7, 8, atau 9 minuman alkohol', 3], 
                    ['10 atau lebih minuman alkohol', 4]
                ]
            }, 
            {
                'question': 'Berapa kerap anda minum enam minuman alkohol atau lebih minuman beralkohol pada satu masa?', 
                'answer': [
                    ['Tak pernah', 0], 
                    ['Kurang dari sekali sebulan', 1], 
                    ['Sekali sebulan', 2], 
                    ['Sekali seminggu', 3], 
                    ['Setiap hari atau hampir setiap hari', 4]
                ]
            }
        ]
    }, 
    'audit-10': {
        'en': [
            {
                'question': 'In the past 12 months, how often do you have a drink containing alcohol?', 
                'answer': [
                    ['Never', 0], 
                    ['Monthly or less', 1], 
                    ['2 to 4 times a month', 2], 
                    ['2 to 3 times a week', 3], 
                    ['4 or more times a week', 4]
                ]
            }, 
            {
                'question': 'How many drinks containing alcohol do you have on a typical day when you are drinking?', 
                'answer': [
                    ['1 or 2', 0], 
                    ['3 or 4', 1], 
                    ['5 or 6', 2], 
                    ['7, 8, or 9', 3], 
                    ['10 or more', 4]
                ]
            }, 
            {
                'question': 'How often do you have six or more drinks on one occasion?', 
                'answer': [
                    ['Never', 0], 
                    ['Less than monthly', 1], 
                    ['Monthly', 2], 
                    ['Weekly', 3], 
                    ['Daily or almost daily', 4]
                ]
            }, 
            {
                'question': 'How often during the past 12 months have you found that you were not able to stop drinking once you had started?', 
                'answer': [
                    ['Never', 0], 
                    ['Less than monthly', 1], 
                    ['Monthly', 2], 
                    ['Weekly', 3], 
                    ['Daily or almost daily', 4]
                ]
            }, 
            {
                'question': 'How often during the past 12 months have you failed to do what was normally expected from you because of drinking?', 
                'answer': [
                    ['Never', 0], 
                    ['Less than monthly', 1], 
                    ['Monthly', 2], 
                    ['Weekly', 3], 
                    ['Daily or almost daily', 4]
                ]
            }, 
            {
                'question': 'How often during the past 12 months have you needed a first drink in the morning to get yourself going after a heavy drinking session?', 
                'answer': [
                    ['Never', 0], 
                    ['Less than monthly', 1], 
                    ['Monthly', 2], 
                    ['Weekly', 3], 
                    ['Daily or almost daily', 4]
                ]
            }, 
            {
                'question': 'How often during the past 12 months have you had a feeling of guilt or remorse after drinking?', 
                'answer': [
                    ['Never', 0], 
                    ['Less than monthly', 1], 
                    ['Monthly', 2], 
                    ['Weekly', 3], 
                    ['Daily or almost daily', 4]
                ]
            }, 
            {
                'question': 'How often during the past 12 months have you been unable to remember what happened the night before because you had been drinking?', 
                'answer': [
                    ['Never', 0], 
                    ['Less than monthly', 1], 
                    ['Monthly', 2], 
                    ['Weekly', 3], 
                    ['Daily or almost daily', 4]
                ]
            }, 
            {
                'question': 'Have you or someone else been injured as a result of your drinking?', 
                'answer': [
                    ['No', 0], 
                    ['Yes, but not in the last year', 2], 
                    ['Yes, during the last year', 4]
                ]
            }, 
            {
                'question': 'Has a relative or friend or a doctor or another health worker been concerned about your drinking or suggested you cut down?', 
                'answer': [
                    ['No', 0], 
                    ['Yes, but not in the last year', 2], 
                    ['Yes, during the last year', 4]
                ]
            }
        ], 
        'ms': [
            {
                'question': 'Dalam tempoh 12 bulan yang lepas berapa kerapkah anda minum minuman keras / arak / beralkohol?', 
                'answer': [
                    ['Tak pernah', 0], 
                    ['Sekali sebulan atau kurang', 1], 
                    ['2-4 kali sebulan', 2], 
                    ['2-3 kali seminggu', 3], 
                    ['4 kali atau lebih seminggu', 4]
                ]
            }, 
            {
                'question': 'Kebiasaannya pada hari yang anda minum, berapa banyakkah anda minum minuman keras / arak / beralkohol?', 
                'answer': [
                    ['1 atau 2', 0], 
                    ['3 atau 4', 1], 
                    ['5 atau 6', 2], 
                    ['7, 8, atau 9', 3], 
                    ['10 atau lebih', 4]
                ]
            }, 
            {
                'question': 'Berapa kerap anda minum enam minuman alkohol atau lebih minuman beralkohol pada satu masa?', 
                'answer': [
                    ['Tak pernah', 0], 
                    ['Kurang dari sekali sebulan', 1], 
                    ['Sekali sebulan', 2], 
                    ['Sekali seminggu', 3], 
                    ['Setiap hari atau hampir setiap hari', 4]
                ]
            }, 
            {
                'question': 'Dalam tempoh 12 bulan yang lepas, berapa kerapkah anda tidak boleh berhenti minum apabila anda mula minum minuman keras / arak / beralkohol?', 
                'answer': [
                    ['Tak pernah', 0], 
                    ['Kurang dari sekali sebulan', 1], 
                    ['Sekali sebulan', 2], 
                    ['Sekali seminggu', 3], 
                    ['Setiap hari atau hampir setiap hari', 4]
                ]
            }, 
            {
                'question': 'Dalam tempoh 12 bulan yang lepas, akibat dari minum minuman keras / arak / beralkohol berapa kerapkah anda tidak boleh melakukan apa yang biasanya anda lakukan?', 
                'answer': [
                    ['Tak pernah', 0], 
                    ['Kurang dari sekali sebulan', 1], 
                    ['Sekali sebulan', 2], 
                    ['Sekali seminggu', 3], 
                    ['Setiap hari atau hampir setiap hari', 4]
                ]
            }, 
            {
                'question': 'Dalam tempoh 12 bulan yang lepas, selepas meminum minuman keras / arak / beralkohol dalam jumlah banyak, berapa kerapkah pada pagi esoknya anda perlu meminum minuman keras / arak / beralkohol sebelum memulakan hari anda?', 
                'answer': [
                    ['Tak pernah', 0], 
                    ['Kurang dari sekali sebulan', 1], 
                    ['Sekali sebulan', 2], 
                    ['Sekali seminggu', 3], 
                    ['Setiap hari atau hampir setiap hari', 4]
                ]
            }, 
            {
                'question': ' Dalam tempoh 12 bulan yang lepas, berapa kerapkah anda rasa bersalah atau menyesal selepas minum minuman keras / arak / beralkohol?', 
                'answer': [
                    ['Tak pernah', 0], 
                    ['Kurang dari sekali sebulan', 1], 
                    ['Sekali sebulan', 2], 
                    ['Sekali seminggu', 3], 
                    ['Setiap hari atau hampir setiap hari', 4]
                ]
            }, 
            {
                'question': 'Dalam tempoh 12 bulan yang lepas, berapa kerapkah anda tidak dapat mengingati apakah yang telah berlaku malam sebelumnya disebabkan anda telah mengambil minuman keras / arak / beralkohol?', 
                'answer': [
                    ['Tak pernah', 0], 
                    ['Kurang dari sekali sebulan', 1], 
                    ['Sekali sebulan', 2], 
                    ['Sekali seminggu', 3], 
                    ['Setiap hari atau hampir setiap hari', 4]
                ]
            }, 
            {
                'question': 'Pernahkah anda atau orang lain tercedera disebabkan anda meminum minuman keras / arak / beralkohol?', 
                'answer': [
                    ['Tidak', 0], 
                    ['Ya, tetapi bukan dalam tempoh setahun yang lepas', 2], 
                    ['Ya, dalam tempoh setahun yang lalu', 4]
                ]
            }, 
            {
                'question': 'Pernahkah saudara anda atau kawan atau doktor atau anggota kesihatan mengambil berat atau mencadangkan supaya anda mengurangkan pengambilan minuman keras / arak/ beralkohol?', 
                'answer': [
                    ['Tidak', 0], 
                    ['Ya, tetapi bukan dalam tempoh setahun yang lepas', 2], 
                    ['Ya, dalam tempoh setahun yang lalu', 4]
                ]
            }
        ]
    }
}
