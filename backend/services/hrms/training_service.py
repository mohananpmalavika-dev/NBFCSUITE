"""
HRMS Training & Development Service Layer
Business logic for training operations
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload
from typing import Optional, List, Tuple, Dict
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

from backend.shared.database.training_models import (
    TrainingCourse, TrainingSession, TrainingParticipant,
    TrainingAssessment, AssessmentResult, TrainingCertification,
    Skill, EmployeeSkill,
    TrainingType, TrainingCategory, TrainingStatus,
    ParticipantStatus, AssessmentType, CertificationStatus, SkillLevel
)
from backend.shared.database.hrms_models import Employee
from .training_schemas import (
    TrainingCourseCreate, TrainingCourseUpdate,
    TrainingSessionCreate, TrainingSessionUpdate,
    TrainingParticipantCreate, TrainingParticipantUpdate,
    TrainingDashboardStats, TrainingCalendarItem
)


class TrainingService:
    """Service for training & development operations"""
    
    def __init__(self, db: AsyncSession, tenant_id: str, user_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    # ========================================================================
    # TRAINING COURSE OPERATIONS
    # ========================================================================
    
    async def generate_course_code(self) -> str:
        """Generate unique course code: TRN-YYYYMM-XXXX"""
        year_month = datetime.now().strftime("%Y%m")
        
        count_query = select(func.count(TrainingCourse.id)).where(
            and_(
                TrainingCourse.tenant_id == self.tenant_id,
                TrainingCourse.course_code.like(f"TRN-{year_month}-%")
            )
        )
        result = await self.db.execute(count_query)
        count = result.scalar() or 0
        
        sequence = str(count + 1).zfill(4)
        return f"TRN-{year_month}-{sequence}"
    
    async def create_training_course(self, data: TrainingCourseCreate) -> TrainingCourse:
        """Create new training course"""
        course_code = await self.generate_course_code()
        
        course = TrainingCourse(
            tenant_id=self.tenant_id,
            course_code=course_code,
            course_name=data.course_name,
            course_description=data.course_description,
            training_type=data.training_type,
            training_category=data.training_category,
            delivery_mode=data.delivery_mode,
            duration_hours=data.duration_hours,
            duration_days=data.duration_days,
            max_participants=data.max_participants,
            min_participants=data.min_participants,
            target_designation_ids=data.target_designation_ids,
            target_department_ids=data.target_department_ids,
            experience_level_required=data.experience_level_required,
            prerequisites=data.prerequisites,
            prerequisite_course_ids=data.prerequisite_course_ids,
            learning_objectives=data.learning_objectives,
            syllabus=data.syllabus,
            internal_trainer_id=data.internal_trainer_id,
            external_trainer_name=data.external_trainer_name,
            external_trainer_organization=data.external_trainer_organization,
            lms_course_id=data.lms_course_id,
            lms_course_url=data.lms_course_url,
            cost_per_participant=data.cost_per_participant,
            currency=data.currency,
            provides_certificate=data.provides_certificate,
            certificate_validity_months=data.certificate_validity_months,
            is_mandatory=data.is_mandatory,
            is_compliance_training=data.is_compliance_training,
            is_active=data.is_active,
            is_published=data.is_published,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(course)
        await self.db.commit()
        await self.db.refresh(course)
        
        return course
    
    async def get_training_course(self, course_id: str) -> Optional[TrainingCourse]:
        """Get training course by ID"""
        query = select(TrainingCourse).where(
            and_(
                TrainingCourse.id == course_id,
                TrainingCourse.tenant_id == self.tenant_id,
                TrainingCourse.is_deleted == False
            )
        ).options(
            selectinload(TrainingCourse.internal_trainer),
            selectinload(TrainingCourse.training_sessions)
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_training_courses(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        training_type: Optional[TrainingType] = None,
        training_category: Optional[TrainingCategory] = None,
        is_active: Optional[bool] = None,
        is_published: Optional[bool] = None,
        is_mandatory: Optional[bool] = None
    ) -> Tuple[List[TrainingCourse], int]:
        """Get paginated list of training courses"""
        
        query = select(TrainingCourse).where(
            and_(
                TrainingCourse.tenant_id == self.tenant_id,
                TrainingCourse.is_deleted == False
            )
        )
        
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    TrainingCourse.course_name.ilike(search_term),
                    TrainingCourse.course_code.ilike(search_term),
                    TrainingCourse.course_description.ilike(search_term)
                )
            )
        
        if training_type:
            query = query.where(TrainingCourse.training_type == training_type)
        
        if training_category:
            query = query.where(TrainingCourse.training_category == training_category)
        
        if is_active is not None:
            query = query.where(TrainingCourse.is_active == is_active)
        
        if is_published is not None:
            query = query.where(TrainingCourse.is_published == is_published)
        
        if is_mandatory is not None:
            query = query.where(TrainingCourse.is_mandatory == is_mandatory)
        
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        query = query.order_by(desc(TrainingCourse.created_at))
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        courses = result.scalars().all()
        
        return courses, total
    
    async def update_training_course(self, course_id: str, data: TrainingCourseUpdate) -> TrainingCourse:
        """Update training course"""
        course = await self.get_training_course(course_id)
        if not course:
            raise ValueError("Training course not found")
        
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(course, field, value)
        
        course.updated_by = self.user_id
        
        await self.db.commit()
        await self.db.refresh(course)
        
        return course
    
    async def delete_training_course(self, course_id: str) -> bool:
        """Soft delete training course"""
        course = await self.get_training_course(course_id)
        if not course:
            raise ValueError("Training course not found")
        
        course.is_deleted = True
        course.deleted_at = datetime.utcnow()
        course.deleted_by = self.user_id
        
        await self.db.commit()
        return True
    
    # ========================================================================
    # TRAINING SESSION OPERATIONS
    # ========================================================================
    
    async def generate_session_code(self) -> str:
        """Generate unique session code: SES-YYYYMM-XXXX"""
        year_month = datetime.now().strftime("%Y%m")
        
        count_query = select(func.count(TrainingSession.id)).where(
            and_(
                TrainingSession.tenant_id == self.tenant_id,
                TrainingSession.session_code.like(f"SES-{year_month}-%")
            )
        )
        result = await self.db.execute(count_query)
        count = result.scalar() or 0
        
        sequence = str(count + 1).zfill(4)
        return f"SES-{year_month}-{sequence}"
    
    async def create_training_session(self, data: TrainingSessionCreate) -> TrainingSession:
        """Create new training session"""
        session_code = await self.generate_session_code()
        
        session = TrainingSession(
            tenant_id=self.tenant_id,
            session_code=session_code,
            session_name=data.session_name,
            course_id=data.course_id,
            start_date=data.start_date,
            end_date=data.end_date,
            start_time=data.start_time,
            end_time=data.end_time,
            location_type=data.location_type,
            venue=data.venue,
            city=data.city,
            address=data.address,
            virtual_meeting_link=data.virtual_meeting_link,
            trainer_id=data.trainer_id,
            external_trainer_name=data.external_trainer_name,
            max_participants=data.max_participants,
            budget_allocated=data.budget_allocated,
            status=data.status,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        
        return session
    
    async def get_training_session(self, session_id: str) -> Optional[TrainingSession]:
        """Get training session by ID"""
        query = select(TrainingSession).where(
            and_(
                TrainingSession.id == session_id,
                TrainingSession.tenant_id == self.tenant_id,
                TrainingSession.is_deleted == False
            )
        ).options(
            selectinload(TrainingSession.course),
            selectinload(TrainingSession.trainer),
            selectinload(TrainingSession.participants)
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_training_sessions(
        self,
        page: int = 1,
        page_size: int = 20,
        course_id: Optional[str] = None,
        status: Optional[TrainingStatus] = None,
        start_date_from: Optional[date] = None,
        start_date_to: Optional[date] = None
    ) -> Tuple[List[TrainingSession], int]:
        """Get paginated list of training sessions"""
        
        query = select(TrainingSession).where(
            and_(
                TrainingSession.tenant_id == self.tenant_id,
                TrainingSession.is_deleted == False
            )
        ).options(
            selectinload(TrainingSession.course)
        )
        
        if course_id:
            query = query.where(TrainingSession.course_id == course_id)
        
        if status:
            query = query.where(TrainingSession.status == status)
        
        if start_date_from:
            query = query.where(TrainingSession.start_date >= start_date_from)
        
        if start_date_to:
            query = query.where(TrainingSession.start_date <= start_date_to)
        
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        query = query.order_by(TrainingSession.start_date)
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        sessions = result.scalars().all()
        
        return sessions, total
    
    async def update_training_session(self, session_id: str, data: TrainingSessionUpdate) -> TrainingSession:
        """Update training session"""
        session = await self.get_training_session(session_id)
        if not session:
            raise ValueError("Training session not found")
        
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(session, field, value)
        
        session.updated_by = self.user_id
        
        await self.db.commit()
        await self.db.refresh(session)
        
        return session
    
    async def get_training_calendar(
        self,
        start_date: date,
        end_date: date
    ) -> List[TrainingCalendarItem]:
        """Get training calendar for date range"""
        query = select(TrainingSession).where(
            and_(
                TrainingSession.tenant_id == self.tenant_id,
                TrainingSession.is_deleted == False,
                TrainingSession.start_date >= start_date,
                TrainingSession.start_date <= end_date,
                TrainingSession.status.in_([TrainingStatus.SCHEDULED, TrainingStatus.IN_PROGRESS])
            )
        ).options(
            selectinload(TrainingSession.course),
            selectinload(TrainingSession.trainer)
        ).order_by(TrainingSession.start_date)
        
        result = await self.db.execute(query)
        sessions = result.scalars().all()
        
        calendar_items = []
        for session in sessions:
            calendar_items.append(TrainingCalendarItem(
                id=str(session.id),
                session_code=session.session_code,
                session_name=session.session_name,
                course_name=session.course.course_name if session.course else "",
                start_date=session.start_date,
                end_date=session.end_date,
                start_time=session.start_time,
                venue=session.venue,
                trainer_name=session.trainer.full_name if session.trainer else session.external_trainer_name,
                enrolled_count=session.enrolled_count,
                max_participants=session.max_participants,
                status=session.status
            ))
        
        return calendar_items
    
    # ========================================================================
    # PARTICIPANT OPERATIONS
    # ========================================================================
    
    async def create_participant(self, data: TrainingParticipantCreate) -> TrainingParticipant:
        """Nominate employee for training"""
        participant = TrainingParticipant(
            tenant_id=self.tenant_id,
            session_id=data.session_id,
            employee_id=data.employee_id,
            nominated_by_id=data.nominated_by_id,
            nomination_reason=data.nomination_reason,
            status=data.status,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(participant)
        
        # Update session enrolled count
        session_query = select(TrainingSession).where(
            TrainingSession.id == data.session_id
        )
        session_result = await self.db.execute(session_query)
        session = session_result.scalar_one_or_none()
        if session:
            session.enrolled_count += 1
        
        await self.db.commit()
        await self.db.refresh(participant)
        
        return participant
    
    async def get_session_participants(
        self,
        session_id: str,
        status: Optional[ParticipantStatus] = None
    ) -> List[TrainingParticipant]:
        """Get participants for a training session"""
        query = select(TrainingParticipant).where(
            and_(
                TrainingParticipant.tenant_id == self.tenant_id,
                TrainingParticipant.session_id == session_id,
                TrainingParticipant.is_deleted == False
            )
        ).options(
            selectinload(TrainingParticipant.employee)
        )
        
        if status:
            query = query.where(TrainingParticipant.status == status)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_participant(
        self,
        participant_id: str,
        data: TrainingParticipantUpdate
    ) -> TrainingParticipant:
        """Update participant status"""
        query = select(TrainingParticipant).where(
            and_(
                TrainingParticipant.id == participant_id,
                TrainingParticipant.tenant_id == self.tenant_id
            )
        )
        result = await self.db.execute(query)
        participant = result.scalar_one_or_none()
        
        if not participant:
            raise ValueError("Participant not found")
        
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(participant, field, value)
        
        participant.updated_by = self.user_id
        
        await self.db.commit()
        await self.db.refresh(participant)
        
        return participant
    
    # ========================================================================
    # CERTIFICATION OPERATIONS
    # ========================================================================
    
    async def generate_certificate_number(self) -> str:
        """Generate unique certificate number: CERT-YYYY-XXXXXX"""
        year = datetime.now().strftime("%Y")
        
        count_query = select(func.count(TrainingCertification.id)).where(
            and_(
                TrainingCertification.tenant_id == self.tenant_id,
                TrainingCertification.certificate_number.like(f"CERT-{year}-%")
            )
        )
        result = await self.db.execute(count_query)
        count = result.scalar() or 0
        
        sequence = str(count + 1).zfill(6)
        return f"CERT-{year}-{sequence}"
    
    async def issue_certificate(
        self,
        employee_id: str,
        course_id: str,
        session_id: Optional[str] = None,
        validity_months: Optional[int] = None
    ) -> TrainingCertification:
        """Issue training certificate to employee"""
        certificate_number = await self.generate_certificate_number()
        
        # Get course details
        course_query = select(TrainingCourse).where(TrainingCourse.id == course_id)
        course_result = await self.db.execute(course_query)
        course = course_result.scalar_one_or_none()
        
        issue_date = date.today()
        expiry_date = None
        if validity_months or (course and course.certificate_validity_months):
            months = validity_months or course.certificate_validity_months
            expiry_date = issue_date + relativedelta(months=months)
        
        certificate = TrainingCertification(
            tenant_id=self.tenant_id,
            certificate_number=certificate_number,
            certificate_name=course.course_name if course else "Training Certification",
            course_id=course_id,
            session_id=session_id,
            employee_id=employee_id,
            issue_date=issue_date,
            expiry_date=expiry_date,
            status=CertificationStatus.ISSUED,
            issued_by_id=self.user_id,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(certificate)
        await self.db.commit()
        await self.db.refresh(certificate)
        
        return certificate
    
    async def get_employee_certifications(
        self,
        employee_id: str
    ) -> List[TrainingCertification]:
        """Get all certifications for an employee"""
        query = select(TrainingCertification).where(
            and_(
                TrainingCertification.tenant_id == self.tenant_id,
                TrainingCertification.employee_id == employee_id,
                TrainingCertification.is_deleted == False
            )
        ).options(
            selectinload(TrainingCertification.course)
        ).order_by(desc(TrainingCertification.issue_date))
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    # ========================================================================
    # SKILL MATRIX OPERATIONS
    # ========================================================================
    
    async def generate_skill_code(self) -> str:
        """Generate unique skill code: SKL-XXXX"""
        count_query = select(func.count(Skill.id)).where(
            Skill.tenant_id == self.tenant_id
        )
        result = await self.db.execute(count_query)
        count = result.scalar() or 0
        
        sequence = str(count + 1).zfill(4)
        return f"SKL-{sequence}"
    
    async def create_skill(
        self,
        skill_name: str,
        skill_category: Optional[str] = None,
        skill_description: Optional[str] = None
    ) -> Skill:
        """Create new skill"""
        skill_code = await self.generate_skill_code()
        
        skill = Skill(
            tenant_id=self.tenant_id,
            skill_code=skill_code,
            skill_name=skill_name,
            skill_description=skill_description,
            skill_category=skill_category,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(skill)
        await self.db.commit()
        await self.db.refresh(skill)
        
        return skill
    
    async def add_employee_skill(
        self,
        employee_id: str,
        skill_id: str,
        proficiency_level: SkillLevel,
        proficiency_percentage: Optional[int] = None
    ) -> EmployeeSkill:
        """Add skill to employee"""
        employee_skill = EmployeeSkill(
            tenant_id=self.tenant_id,
            employee_id=employee_id,
            skill_id=skill_id,
            proficiency_level=proficiency_level,
            proficiency_percentage=proficiency_percentage,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(employee_skill)
        await self.db.commit()
        await self.db.refresh(employee_skill)
        
        return employee_skill
    
    async def get_employee_skills(
        self,
        employee_id: str
    ) -> List[EmployeeSkill]:
        """Get all skills for an employee"""
        query = select(EmployeeSkill).where(
            and_(
                EmployeeSkill.tenant_id == self.tenant_id,
                EmployeeSkill.employee_id == employee_id,
                EmployeeSkill.is_deleted == False,
                EmployeeSkill.is_active == True
            )
        ).options(
            selectinload(EmployeeSkill.skill)
        )
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_skill_matrix(
        self,
        department_id: Optional[str] = None,
        skill_category: Optional[str] = None
    ) -> Dict:
        """Get skill matrix report"""
        # This would return a matrix of employees vs skills with proficiency levels
        # Implementation would depend on specific reporting requirements
        pass
    
    # ========================================================================
    # DASHBOARD & STATISTICS
    # ========================================================================
    
    async def get_dashboard_stats(self) -> TrainingDashboardStats:
        """Get training dashboard statistics"""
        
        # Total courses
        total_courses_query = select(func.count(TrainingCourse.id)).where(
            and_(
                TrainingCourse.tenant_id == self.tenant_id,
                TrainingCourse.is_deleted == False
            )
        )
        total_courses_result = await self.db.execute(total_courses_query)
        total_courses = total_courses_result.scalar() or 0
        
        # Active courses
        active_courses_query = select(func.count(TrainingCourse.id)).where(
            and_(
                TrainingCourse.tenant_id == self.tenant_id,
                TrainingCourse.is_deleted == False,
                TrainingCourse.is_active == True
            )
        )
        active_courses_result = await self.db.execute(active_courses_query)
        active_courses = active_courses_result.scalar() or 0
        
        # Total sessions
        total_sessions_query = select(func.count(TrainingSession.id)).where(
            and_(
                TrainingSession.tenant_id == self.tenant_id,
                TrainingSession.is_deleted == False
            )
        )
        total_sessions_result = await self.db.execute(total_sessions_query)
        total_sessions = total_sessions_result.scalar() or 0
        
        # Upcoming sessions
        today = date.today()
        upcoming_sessions_query = select(func.count(TrainingSession.id)).where(
            and_(
                TrainingSession.tenant_id == self.tenant_id,
                TrainingSession.is_deleted == False,
                TrainingSession.start_date >= today,
                TrainingSession.status == TrainingStatus.SCHEDULED
            )
        )
        upcoming_sessions_result = await self.db.execute(upcoming_sessions_query)
        upcoming_sessions = upcoming_sessions_result.scalar() or 0
        
        # Ongoing sessions
        ongoing_sessions_query = select(func.count(TrainingSession.id)).where(
            and_(
                TrainingSession.tenant_id == self.tenant_id,
                TrainingSession.is_deleted == False,
                TrainingSession.status == TrainingStatus.IN_PROGRESS
            )
        )
        ongoing_sessions_result = await self.db.execute(ongoing_sessions_query)
        ongoing_sessions = ongoing_sessions_result.scalar() or 0
        
        # Completed sessions
        completed_sessions_query = select(func.count(TrainingSession.id)).where(
            and_(
                TrainingSession.tenant_id == self.tenant_id,
                TrainingSession.is_deleted == False,
                TrainingSession.status == TrainingStatus.COMPLETED
            )
        )
        completed_sessions_result = await self.db.execute(completed_sessions_query)
        completed_sessions = completed_sessions_result.scalar() or 0
        
        # Total participants
        total_participants_query = select(func.count(TrainingParticipant.id)).where(
            and_(
                TrainingParticipant.tenant_id == self.tenant_id,
                TrainingParticipant.is_deleted == False
            )
        )
        total_participants_result = await self.db.execute(total_participants_query)
        total_participants = total_participants_result.scalar() or 0
        
        # Certifications issued
        certifications_query = select(func.count(TrainingCertification.id)).where(
            and_(
                TrainingCertification.tenant_id == self.tenant_id,
                TrainingCertification.is_deleted == False,
                TrainingCertification.status == CertificationStatus.ISSUED
            )
        )
        certifications_result = await self.db.execute(certifications_query)
        certifications_issued = certifications_result.scalar() or 0
        
        return TrainingDashboardStats(
            total_courses=total_courses,
            active_courses=active_courses,
            total_sessions=total_sessions,
            upcoming_sessions=upcoming_sessions,
            ongoing_sessions=ongoing_sessions,
            completed_sessions=completed_sessions,
            total_participants=total_participants,
            certifications_issued=certifications_issued
        )
