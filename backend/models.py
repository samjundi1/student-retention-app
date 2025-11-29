from pydantic import BaseModel

class StudentData(BaseModel):
    FirstTermGPA: float
    SecondTermGPA: float
    HighSchoolAverageMark: float
    MathScore: float
    FirstLanguage: int
    Funding: int
    School: int
    FastTrack: int
    Coop: int
    Residency: int
    Gender: int
    PrevEducation: int
    AgeGroup: int
    EnglishGrade: int