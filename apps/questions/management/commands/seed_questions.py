from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.questions.models import Class, Group, Subject, Chapter, Topic, Question, MCQOption, CQSubQuestion
from decimal import Decimal

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed database with comprehensive question data for all classes and subjects'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting database seeding...'))
        
        # Get or create admin user for created_by field
        user, created = User.objects.get_or_create(
            email='admin@pronoyon.com',
            defaults={
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            user.set_password('admin123')
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Created admin user: {user.email}'))
        
        # Seed Classes
        self.stdout.write('Creating classes...')
        class_6 = self.create_class(user, 'Class 6', 'CLS6', 6, False)
        class_7 = self.create_class(user, 'Class 7', 'CLS7', 7, False)
        class_8 = self.create_class(user, 'Class 8', 'CLS8', 8, False)
        class_9 = self.create_class(user, 'Class 9', 'CLS9', 9, False)
        class_10 = self.create_class(user, 'Class 10', 'CLS10', 10, False)
        hsc = self.create_class(user, 'HSC', 'HSC', 12, True)
        admission = self.create_class(user, 'Admission', 'ADM', 13, True)
        
        # Seed Groups for HSC and Admission
        self.stdout.write('Creating groups...')
        hsc_science = self.create_group(user, hsc, 'Science', 'SCI', Group.SCIENCE, 1)
        hsc_arts = self.create_group(user, hsc, 'Arts', 'ARTS', Group.ARTS, 2)
        hsc_commerce = self.create_group(user, hsc, 'Commerce', 'COM', Group.COMMERCE, 3)
        
        adm_science = self.create_group(user, admission, 'Science', 'SCI', Group.SCIENCE, 1)
        adm_arts = self.create_group(user, admission, 'Arts', 'ARTS', Group.ARTS, 2)
        adm_commerce = self.create_group(user, admission, 'Commerce', 'COM', Group.COMMERCE, 3)
        
        # Seed Subjects and Questions
        self.stdout.write('Creating subjects and questions...')
        
        # Class 6-10 subjects (no groups)
        self.seed_class_6_10(user, class_6, class_7, class_8, class_9, class_10)
        
        # HSC subjects with groups
        self.seed_hsc(user, hsc, hsc_science, hsc_arts, hsc_commerce)
        
        # Admission subjects with groups
        self.seed_admission(user, admission, adm_science, adm_arts, adm_commerce)
        
        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))
        self.stdout.write(self.style.SUCCESS(f'Total Classes: {Class.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Total Groups: {Group.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Total Subjects: {Subject.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Total Chapters: {Chapter.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Total Topics: {Topic.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Total Questions: {Question.objects.count()}'))
    
    def create_class(self, user, name, code, order, has_groups):
        class_obj, created = Class.objects.get_or_create(
            name=name,
            defaults={
                'code': code,
                'order': order,
                'has_groups': has_groups,
                'created_by': user
            }
        )
        if created:
            self.stdout.write(f'  ✓ Created class: {name}')
        return class_obj
    
    def create_group(self, user, class_level, name, code, group_type, order):
        group, created = Group.objects.get_or_create(
            class_level=class_level,
            name=name,
            defaults={
                'code': code,
                'group_type': group_type,
                'order': order,
                'created_by': user
            }
        )
        if created:
            self.stdout.write(f'  ✓ Created group: {class_level.name} - {name}')
        return group
    
    def create_subject(self, user, class_level, name, code, order, group=None):
        subject, created = Subject.objects.get_or_create(
            class_level=class_level,
            group=group,
            name=name,
            defaults={
                'code': code,
                'order': order,
                'created_by': user
            }
        )
        if created:
            group_name = f' ({group.name})' if group else ''
            self.stdout.write(f'  ✓ Created subject: {name}{group_name}')
        return subject
    
    def create_chapter(self, user, subject, name, order):
        chapter, created = Chapter.objects.get_or_create(
            subject=subject,
            name=name,
            defaults={
                'order': order,
                'created_by': user
            }
        )
        return chapter
    
    def create_topic(self, user, chapter, name, order):
        topic, created = Topic.objects.get_or_create(
            chapter=chapter,
            name=name,
            defaults={
                'order': order,
                'created_by': user
            }
        )
        return topic
    
    def create_mcq_simple(self, user, subject, topic, question_text, options, marks=1, difficulty='easy', solution=''):
        question = Question.objects.create(
            type=Question.MCQ,
            mcq_subtype=Question.SIMPLE,
            question_text=question_text,
            marks=marks,
            difficulty=difficulty,
            subject=subject,
            solution=solution,
            created_by=user
        )
        question.topics.add(topic)
        
        for opt in options:
            MCQOption.objects.create(
                question=question,
                option_text=opt['text'],
                option_label=opt['label'],
                is_correct=opt['correct'],
                order=opt['order']
            )
        return question
    
    def create_mcq_combined(self, user, subject, topic, question_text, options, marks=1, difficulty='medium'):
        question = Question.objects.create(
            type=Question.MCQ,
            mcq_subtype=Question.COMBINED,
            question_text=question_text,
            marks=marks,
            difficulty=difficulty,
            subject=subject,
            created_by=user
        )
        question.topics.add(topic)
        
        for opt in options:
            MCQOption.objects.create(
                question=question,
                option_text=opt['text'],
                option_label=opt['label'],
                is_correct=opt['correct'],
                order=opt['order'],
                combined_option_indices=opt.get('indices', [])
            )
        return question
    
    def create_cq(self, user, subject, topic, question_text, sub_questions, total_marks=10, difficulty='hard'):
        question = Question.objects.create(
            type=Question.CQ,
            question_text=question_text,
            marks=total_marks,
            difficulty=difficulty,
            subject=subject,
            created_by=user
        )
        question.topics.add(topic)
        
        for sq in sub_questions:
            CQSubQuestion.objects.create(
                question=question,
                label=sq['label'],
                sub_question_text=sq['text'],
                marks=sq['marks'],
                answer=sq['answer'],
                order=sq['order']
            )
        return question
    
    def seed_class_6_10(self, user, class_6, class_7, class_8, class_9, class_10):
        """Seed questions for Class 6-10"""
        
        # Mathematics for Class 6
        math_6 = self.create_subject(user, class_6, 'Mathematics', 'MATH6', 1)
        math_ch1 = self.create_chapter(user, math_6, 'Number Systems', 1)
        math_topic1 = self.create_topic(user, math_ch1, 'Natural Numbers', 1)
        
        self.create_mcq_simple(user, math_6, math_topic1,
            'What is the result of $5 + 7$?',
            [
                {'text': '$12$', 'label': 'A', 'correct': True, 'order': 1},
                {'text': '$10$', 'label': 'B', 'correct': False, 'order': 2},
                {'text': '$11$', 'label': 'C', 'correct': False, 'order': 3},
                {'text': '$13$', 'label': 'D', 'correct': False, 'order': 4}
            ],
            solution='$5 + 7 = 12$'
        )
        
        self.create_mcq_simple(user, math_6, math_topic1,
            'Which number is **even**?',
            [
                {'text': '$3$', 'label': 'A', 'correct': False, 'order': 1},
                {'text': '$8$', 'label': 'B', 'correct': True, 'order': 2},
                {'text': '$5$', 'label': 'C', 'correct': False, 'order': 3},
                {'text': '$7$', 'label': 'D', 'correct': False, 'order': 4}
            ]
        )
        
        self.create_mcq_combined(user, math_6, math_topic1,
            'নিচের কোনটি সঠিক?\n\ni. $2 + 2 = 4$\nii. $3 \\times 3 = 9$\niii. $5 - 2 = 3$',
            [
                {'text': 'i ও ii', 'label': 'ক', 'correct': False, 'order': 1, 'indices': [0, 1]},
                {'text': 'i ও iii', 'label': 'খ', 'correct': False, 'order': 2, 'indices': [0, 2]},
                {'text': 'ii ও iii', 'label': 'গ', 'correct': False, 'order': 3, 'indices': [1, 2]},
                {'text': 'i, ii ও iii', 'label': 'ঘ', 'correct': True, 'order': 4, 'indices': [0, 1, 2]}
            ]
        )
        
        # Science for Class 6
        science_6 = self.create_subject(user, class_6, 'Science', 'SCI6', 2)
        science_ch1 = self.create_chapter(user, science_6, 'Living Organisms', 1)
        science_topic1 = self.create_topic(user, science_ch1, 'Plants and Animals', 1)
        
        self.create_mcq_simple(user, science_6, science_topic1,
            'Which organ pumps blood in the human body?',
            [
                {'text': 'Brain', 'label': 'A', 'correct': False, 'order': 1},
                {'text': 'Heart', 'label': 'B', 'correct': True, 'order': 2},
                {'text': 'Liver', 'label': 'C', 'correct': False, 'order': 3},
                {'text': 'Kidney', 'label': 'D', 'correct': False, 'order': 4}
            ],
            solution='The heart is the organ that pumps blood throughout the body.'
        )
        
        # Bangla for Class 6
        bangla_6 = self.create_subject(user, class_6, 'Bangla', 'BAN6', 3)
        bangla_ch1 = self.create_chapter(user, bangla_6, 'কবিতা', 1)
        bangla_topic1 = self.create_topic(user, bangla_ch1, 'ছন্দ', 1)
        
        self.create_mcq_simple(user, bangla_6, bangla_topic1,
            'বাংলা বর্ণমালায় মোট কতটি বর্ণ আছে?',
            [
                {'text': '$৫০$', 'label': 'ক', 'correct': True, 'order': 1},
                {'text': '$৪৮$', 'label': 'খ', 'correct': False, 'order': 2},
                {'text': '$৫২$', 'label': 'গ', 'correct': False, 'order': 3},
                {'text': '$৪৬$', 'label': 'ঘ', 'correct': False, 'order': 4}
            ]
        )
        
        # English for Class 6
        english_6 = self.create_subject(user, class_6, 'English', 'ENG6', 4)
        english_ch1 = self.create_chapter(user, english_6, 'Grammar', 1)
        english_topic1 = self.create_topic(user, english_ch1, 'Parts of Speech', 1)
        
        self.create_mcq_simple(user, english_6, english_topic1,
            'Which of the following is a **noun**?',
            [
                {'text': 'Run', 'label': 'A', 'correct': False, 'order': 1},
                {'text': 'Beautiful', 'label': 'B', 'correct': False, 'order': 2},
                {'text': 'Cat', 'label': 'C', 'correct': True, 'order': 3},
                {'text': 'Quickly', 'label': 'D', 'correct': False, 'order': 4}
            ]
        )
        
        # Add similar patterns for Class 7-10
        for cls in [class_7, class_8, class_9, class_10]:
            math_subj = self.create_subject(user, cls, 'Mathematics', f'MATH{cls.code[-1]}', 1)
            science_subj = self.create_subject(user, cls, 'Science', f'SCI{cls.code[-1]}', 2)
            bangla_subj = self.create_subject(user, cls, 'Bangla', f'BAN{cls.code[-1]}', 3)
            english_subj = self.create_subject(user, cls, 'English', f'ENG{cls.code[-1]}', 4)
            
            # Add a few questions for each
            for subj in [math_subj, science_subj, bangla_subj, english_subj]:
                ch = self.create_chapter(user, subj, 'Chapter 1', 1)
                topic = self.create_topic(user, ch, 'Topic 1', 1)
                
                self.create_mcq_simple(user, subj, topic,
                    f'Sample question for {subj.name} {cls.name}?',
                    [
                        {'text': 'Option A', 'label': 'A', 'correct': True, 'order': 1},
                        {'text': 'Option B', 'label': 'B', 'correct': False, 'order': 2},
                        {'text': 'Option C', 'label': 'C', 'correct': False, 'order': 3},
                        {'text': 'Option D', 'label': 'D', 'correct': False, 'order': 4}
                    ]
                )
    
    def seed_hsc(self, user, hsc, science, arts, commerce):
        """Seed HSC subjects and questions"""
        
        # Science Group - Physics
        physics = self.create_subject(user, hsc, 'Physics', 'PHY', 1, science)
        physics_ch1 = self.create_chapter(user, physics, 'Mechanics', 1)
        physics_topic1 = self.create_topic(user, physics_ch1, "Newton's Laws of Motion", 1)
        
        self.create_mcq_simple(user, physics, physics_topic1,
            'What is the acceleration due to gravity on Earth? ($g$)',
            [
                {'text': '$9.8 \\, m/s^2$', 'label': 'A', 'correct': True, 'order': 1},
                {'text': '$8.9 \\, m/s^2$', 'label': 'B', 'correct': False, 'order': 2},
                {'text': '$10.0 \\, m/s^2$', 'label': 'C', 'correct': False, 'order': 3},
                {'text': '$9.0 \\, m/s^2$', 'label': 'D', 'correct': False, 'order': 4}
            ],
            marks=1,
            difficulty='easy',
            solution='The standard acceleration due to gravity on Earth is $g = 9.8 \\, m/s^2$'
        )
        
        self.create_mcq_simple(user, physics, physics_topic1,
            'According to **Newton\'s Second Law**, $F = ma$. If force is doubled and mass remains constant, acceleration will:',
            [
                {'text': 'Double', 'label': 'A', 'correct': True, 'order': 1},
                {'text': 'Halve', 'label': 'B', 'correct': False, 'order': 2},
                {'text': 'Quadruple', 'label': 'C', 'correct': False, 'order': 3},
                {'text': 'Remain same', 'label': 'D', 'correct': False, 'order': 4}
            ],
            marks=1,
            difficulty='medium'
        )
        
        self.create_mcq_combined(user, physics, physics_topic1,
            'নিউটনের সূত্র সম্পর্কে:\n\ni. প্রথম সূত্র জড়তার সূত্র\nii. দ্বিতীয় সূত্র $F = ma$\niii. তৃতীয় সূত্র ক্রিয়া-প্রতিক্রিয়া\n\nনিচের কোনটি সঠিক?',
            [
                {'text': 'i ও ii', 'label': 'ক', 'correct': False, 'order': 1, 'indices': [0, 1]},
                {'text': 'i ও iii', 'label': 'খ', 'correct': False, 'order': 2, 'indices': [0, 2]},
                {'text': 'ii ও iii', 'label': 'গ', 'correct': False, 'order': 3, 'indices': [1, 2]},
                {'text': 'i, ii ও iii', 'label': 'ঘ', 'correct': True, 'order': 4, 'indices': [0, 1, 2]}
            ],
            marks=1,
            difficulty='medium'
        )
        
        self.create_cq(user, physics, physics_topic1,
            'একটি $2 \\, kg$ ভরের বস্তুর উপর $10 \\, N$ বল প্রয়োগ করা হলো।',
            [
                {'label': 'a', 'text': 'বলের সংজ্ঞা লিখুন।', 'marks': Decimal('2'), 
                 'answer': 'বল হলো এমন একটি বাহ্যিক প্রভাব যা স্থির বস্তুকে গতিশীল বা গতিশীল বস্তুকে স্থির করতে পারে।', 'order': 1},
                {'label': 'b', 'text': 'বস্তুর ত্বরণ নির্ণয় করুন।', 'marks': Decimal('4'),
                 'answer': '$F = ma$ সূত্র থেকে, $a = \\frac{F}{m} = \\frac{10}{2} = 5 \\, m/s^2$', 'order': 2},
                {'label': 'c', 'text': 'নিউটনের দ্বিতীয় সূত্র ব্যাখ্যা করুন।', 'marks': Decimal('4'),
                 'answer': 'নিউটনের দ্বিতীয় সূত্র অনুযায়ী, কোনো বস্তুর উপর প্রযুক্ত বল বস্তুর ভর ও ত্বরণের গুণফলের সমান। $F = ma$', 'order': 3}
            ],
            total_marks=Decimal('10'),
            difficulty='hard'
        )
        
        # Chemistry
        chemistry = self.create_subject(user, hsc, 'Chemistry', 'CHEM', 2, science)
        chem_ch1 = self.create_chapter(user, chemistry, 'Organic Chemistry', 1)
        chem_topic1 = self.create_topic(user, chem_ch1, 'Hydrocarbons', 1)
        
        self.create_mcq_simple(user, chemistry, chem_topic1,
            'What is the general formula of alkanes?',
            [
                {'text': '$C_nH_{2n+2}$', 'label': 'A', 'correct': True, 'order': 1},
                {'text': '$C_nH_{2n}$', 'label': 'B', 'correct': False, 'order': 2},
                {'text': '$C_nH_{2n-2}$', 'label': 'C', 'correct': False, 'order': 3},
                {'text': '$C_nH_n$', 'label': 'D', 'correct': False, 'order': 4}
            ],
            difficulty='medium'
        )
        
        # Mathematics (Science)
        math_sci = self.create_subject(user, hsc, 'Higher Mathematics', 'HMATH', 3, science)
        math_ch1 = self.create_chapter(user, math_sci, 'Calculus', 1)
        math_topic1 = self.create_topic(user, math_ch1, 'Differentiation', 1)
        
        self.create_mcq_simple(user, math_sci, math_topic1,
            'What is the derivative of $x^2$?',
            [
                {'text': '$2x$', 'label': 'A', 'correct': True, 'order': 1},
                {'text': '$x$', 'label': 'B', 'correct': False, 'order': 2},
                {'text': '$2x^2$', 'label': 'C', 'correct': False, 'order': 3},
                {'text': '$x^2$', 'label': 'D', 'correct': False, 'order': 4}
            ]
        )
        
        # Arts Group - History
        history = self.create_subject(user, hsc, 'History', 'HIST', 1, arts)
        hist_ch1 = self.create_chapter(user, history, 'Ancient History', 1)
        hist_topic1 = self.create_topic(user, hist_ch1, 'Civilizations', 1)
        
        self.create_mcq_simple(user, history, hist_topic1,
            'When did the **Liberation War of Bangladesh** take place?',
            [
                {'text': '1970', 'label': 'A', 'correct': False, 'order': 1},
                {'text': '1971', 'label': 'B', 'correct': True, 'order': 2},
                {'text': '1972', 'label': 'C', 'correct': False, 'order': 3},
                {'text': '1973', 'label': 'D', 'correct': False, 'order': 4}
            ]
        )
        
        # Civics
        civics = self.create_subject(user, hsc, 'Civics', 'CIV', 2, arts)
        civ_ch1 = self.create_chapter(user, civics, 'Government Systems', 1)
        civ_topic1 = self.create_topic(user, civ_ch1, 'Democracy', 1)
        
        self.create_mcq_simple(user, civics, civ_topic1,
            'What type of government does Bangladesh have?',
            [
                {'text': 'Presidential', 'label': 'A', 'correct': False, 'order': 1},
                {'text': 'Parliamentary', 'label': 'B', 'correct': True, 'order': 2},
                {'text': 'Monarchy', 'label': 'C', 'correct': False, 'order': 3},
                {'text': 'Federal', 'label': 'D', 'correct': False, 'order': 4}
            ]
        )
        
        # Commerce Group - Accounting
        accounting = self.create_subject(user, hsc, 'Accounting', 'ACC', 1, commerce)
        acc_ch1 = self.create_chapter(user, accounting, 'Introduction to Accounting', 1)
        acc_topic1 = self.create_topic(user, acc_ch1, 'Basic Concepts', 1)
        
        self.create_mcq_simple(user, accounting, acc_topic1,
            'What is the **accounting equation**?',
            [
                {'text': 'Assets = Liabilities + Equity', 'label': 'A', 'correct': True, 'order': 1},
                {'text': 'Assets = Equity - Liabilities', 'label': 'B', 'correct': False, 'order': 2},
                {'text': 'Assets + Liabilities = Equity', 'label': 'C', 'correct': False, 'order': 3},
                {'text': 'Assets = Liabilities', 'label': 'D', 'correct': False, 'order': 4}
            ]
        )
        
        # Business Studies
        business = self.create_subject(user, hsc, 'Business Studies', 'BUS', 2, commerce)
        bus_ch1 = self.create_chapter(user, business, 'Introduction to Business', 1)
        bus_topic1 = self.create_topic(user, bus_ch1, 'Business Concepts', 1)
        
        self.create_mcq_simple(user, business, bus_topic1,
            'What is the primary objective of a business?',
            [
                {'text': 'Social service', 'label': 'A', 'correct': False, 'order': 1},
                {'text': 'Profit maximization', 'label': 'B', 'correct': True, 'order': 2},
                {'text': 'Government support', 'label': 'C', 'correct': False, 'order': 3},
                {'text': 'Employee welfare', 'label': 'D', 'correct': False, 'order': 4}
            ]
        )
    
    def seed_admission(self, user, admission, science, arts, commerce):
        """Seed Admission test questions"""
        
        # Science Group
        physics_adm = self.create_subject(user, admission, 'Physics', 'PHY', 1, science)
        physics_ch = self.create_chapter(user, physics_adm, 'Advanced Mechanics', 1)
        physics_topic = self.create_topic(user, physics_ch, 'Motion', 1)
        
        self.create_mcq_simple(user, physics_adm, physics_topic,
            'A body of mass $5 \\, kg$ is moving with velocity $10 \\, m/s$. What is its kinetic energy?',
            [
                {'text': '$250 \\, J$', 'label': 'A', 'correct': True, 'order': 1},
                {'text': '$500 \\, J$', 'label': 'B', 'correct': False, 'order': 2},
                {'text': '$125 \\, J$', 'label': 'C', 'correct': False, 'order': 3},
                {'text': '$50 \\, J$', 'label': 'D', 'correct': False, 'order': 4}
            ],
            difficulty='hard',
            solution='$KE = \\frac{1}{2}mv^2 = \\frac{1}{2} \\times 5 \\times 10^2 = 250 \\, J$'
        )
        
        # Math for Admission
        math_adm = self.create_subject(user, admission, 'Mathematics', 'MATH', 2, science)
        math_ch = self.create_chapter(user, math_adm, 'Algebra', 1)
        math_topic = self.create_topic(user, math_ch, 'Equations', 1)
        
        self.create_mcq_simple(user, math_adm, math_topic,
            'Solve: $x^2 - 5x + 6 = 0$',
            [
                {'text': '$x = 2, 3$', 'label': 'A', 'correct': True, 'order': 1},
                {'text': '$x = 1, 6$', 'label': 'B', 'correct': False, 'order': 2},
                {'text': '$x = -2, -3$', 'label': 'C', 'correct': False, 'order': 3},
                {'text': '$x = 0, 5$', 'label': 'D', 'correct': False, 'order': 4}
            ],
            difficulty='medium'
        )
        
        # Arts group
        history_adm = self.create_subject(user, admission, 'History', 'HIST', 1, arts)
        hist_ch = self.create_chapter(user, history_adm, 'Bangladesh History', 1)
        hist_topic = self.create_topic(user, hist_ch, 'Liberation War', 1)
        
        self.create_mcq_simple(user, history_adm, hist_topic,
            'Who is the **Father of the Nation** of Bangladesh?',
            [
                {'text': 'Ziaur Rahman', 'label': 'A', 'correct': False, 'order': 1},
                {'text': 'Bangabandhu Sheikh Mujibur Rahman', 'label': 'B', 'correct': True, 'order': 2},
                {'text': 'Hussain Muhammad Ershad', 'label': 'C', 'correct': False, 'order': 3},
                {'text': 'Tajuddin Ahmad', 'label': 'D', 'correct': False, 'order': 4}
            ]
        )
        
        # Commerce group
        accounting_adm = self.create_subject(user, admission, 'Accounting', 'ACC', 1, commerce)
        acc_ch = self.create_chapter(user, accounting_adm, 'Financial Accounting', 1)
        acc_topic = self.create_topic(user, acc_ch, 'Journal Entries', 1)
        
        self.create_mcq_simple(user, accounting_adm, acc_topic,
            'Double entry system was introduced by:',
            [
                {'text': 'Adam Smith', 'label': 'A', 'correct': False, 'order': 1},
                {'text': 'Luca Pacioli', 'label': 'B', 'correct': True, 'order': 2},
                {'text': 'J.M. Keynes', 'label': 'C', 'correct': False, 'order': 3},
                {'text': 'Alfred Marshall', 'label': 'D', 'correct': False, 'order': 4}
            ]
        )
