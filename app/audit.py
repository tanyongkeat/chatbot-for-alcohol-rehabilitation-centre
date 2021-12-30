assessment = {
    'audit-c': {
        'en': [
            {
                'question': 'Within the past year, how often did you have a drink of alcohol?', 
                'answer': [
                    ['Never', 0], 
                    ['Monthly', 1], 
                    ['2-4 times a month', 2], 
                    ['2-3 times a week', 3], 
                    ['4 or more times a week', 4]
                ]
            }, 
            {
                'question': 'Within the past year, how many standard drinks containing alcohol did you have on a typical day?', 
                'answer': [
                    ['1 or 2', 0], 
                    ['3 or 4', 1], 
                    ['5 or 6', 2], 
                    ['7 to 9', 3], 
                    ['10 or more', 4]
                ]
            }, 
            {
                'question': 'Within the past year, how often did you have six or more drinks on one occasion?', 
                'answer': [
                    ['Never', 0], 
                    ['Less than monthly', 1], 
                    ['Monthly', 2], 
                    ['Weekly', 3], 
                    ['Daily or almost daily', 4]
                ]
            }, 
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
                'question': 'How often during the last year have you found that you were not able to stop drinking once you had started?', 
                'answer': [
                    ['Never', 0], 
                    ['Less than monthly', 1], 
                    ['Monthly', 2], 
                    ['Weekly', 3], 
                    ['Daily or almost daily', 4]
                ]
            }, 
            {
                'question': 'How often during the last year have you failed to do what was normally expected from you because of drinking?', 
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
                'question': 'How often during the last year have you had a feeling of guilt or remorse after drinking?', 
                'answer': [
                    ['Never', 0], 
                    ['Less than monthly', 1], 
                    ['Monthly', 2], 
                    ['Weekly', 3], 
                    ['Daily or almost daily', 4]
                ]
            }, 
            {
                'question': 'How often during the last year have you been unable to remember what happened the night before because you had been drinking?', 
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
        ]
    }
}

def assessment_flow(assessment, results):
    print(assessment, results)

    score = 0

    if assessment == 'audit-c':
        n_question = 3
        for i in range(n_question):
            if str(i) not in results:
                return 'audit-c error'
            score += results[str(i)]
        
        if score > 4:
            return 'audit-c high risk'
        if score > 2:
            return 'audit-c medium risk'
        return 'audit-c low risk'
    
    if assessment == 'audit-10':
        n_question = 10
        for i in range(n_question):
            if str(i) not in results:
                return 'audit-10 error'
            score += results[str(i)]
        
        if score > 14:
            return 'audit-10 >= 15'
        return 'audit-10 < 15'
    
    return 'audit-c results'