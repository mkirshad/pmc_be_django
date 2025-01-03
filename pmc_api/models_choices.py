GENDER_CHOICES = (
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Rather not say', 'Rather not say'),
)
MOBILE_NETWORK_CHOICES = (
    ('Mobilink', 'Mobilink'),
    ('Telenor', 'Telenor'),
    ('Ufone', 'Ufone'),
    ('Warid', 'Warid'),
)
# APPLICANT > LSO > LSM > DO > LSM2 > TL > DEO > Download License
USER_GROUPS = (
    ('APPLICANT', 'APPLICANT'),
    ('LSO', 'LSO'),
    ('LSO1', 'LSO1'),
    ('LSO2', 'LSO2'),
    ('LSO3', 'LSO3'),
    ('LSM', 'LSM'),
    ('DO', 'DO'),
    ('LSM2','LSM'),
    ('TL', 'TL'),
    ('DEO', 'DEO'),
    ('Download License','Download License')
)
REG_TYPE_CHOICES = [
    ('Producer', 'Producer'),
    ('Consumer', 'Consumer'),
    ('Recycler', 'Recycler'),
    ('Collector', 'Collector'),
]
APPLICATION_STATUS_CHOICES = [
    ('Created', 'Created'),
    ('Fee Challan', 'Fee Challan'),
    ('Submitted', 'Submitted'),
    ('In Review', 'In Review'),
    ('Approved', 'Approved'),
    ('Rejected', 'Rejected'),
    ('In Process', 'In Process'),
    ('Completed', 'Completed'),
]
ENTITY_TYPE_CHOICES = [
    ('Individual', 'Individual'),
    ('Company', 'Company/Corporation/Partnership'),
]

BUSINESS_REGISTRATION_CHOICES = [
    ('sole_proprietorship', 'Sole Proprietorship'),
    ('aop', 'Association of Persons (AOP)'),
    ('public_ltd', 'Limited Company: Public Ltd'),
    ('private_ltd', 'Limited Company: Private Ltd'),
    ('single_member', 'Limited Company: Single Member'),
]
REGISTRATION_CHOICES = [
    ('carry_bags', 'Carry bags'),
    ('sup', 'Single-use Plastics'),
    ('plastic_packaging', 'Plastic Packaging')
]

COMPLIANCE_CHOICES = [('yes', 'Yes'), ('no', 'No')]

IMPORT_BOUGHT = [
    ('imported', 'Imported'),
    ('bought', 'Bought')
]
UNITS_CHOICES = [
    ('kg_per_day', 'Kg/day'),
    ('ton_per_day', 'Ton/day'),
]
DISPOSAL_SOURCES = [
    ('Recycler', 'Recycler'),
    ('Landfill Site', 'Landfill Site'),
    ('Incinerators', 'Incinerators'),
]

fee_structure = {
    'Producer': {
        'upto_5_machines': 50000,
        'from_6_to_10_machines': 100000,
        'more_than_10_machines': 300000,
    },
    'Distributor': {'Company': 200000, 'Individual': 100000},
    'Consumer': {'Company': 200000, 'Individual': 100000},
    'Collector': {'Company': 1000, 'Individual': 500},
    'Recycler': {'Company': 50000, 'Individual': 25000},
}