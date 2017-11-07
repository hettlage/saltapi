from data.proposals import *
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from data.common import Semester as TypeSemester, conn
import pandas as pd
from graphene import relay, Field, String, Boolean
from flask import g


class ProposalGeneralInfo(SQLAlchemyObjectType):
    class Meta:
        interfaces = (relay.Node, )
        model = ProposalGeneralInfoModel

    is_p4 = Boolean()

    def resolve_is_p4(self, args, context, info):
        return ProposalGeneralInfoModel.P4 == 1


class Partner(SQLAlchemyObjectType):
    class Meta:
        interfaces = (relay.Node, )
        model = PartnerModel


class MultiPartner(SQLAlchemyObjectType):
    class Meta:
        interfaces = (relay.Node, )
        model = MultiPartnerModel


class Proposal(SQLAlchemyObjectType):
    class Meta:
        interfaces = (relay.Node, )
        model = ProposalModel
    proposal_id = ProposalModel.Proposal_Id
    ProposalCode_Id = ProposalModel.ProposalCode_Id
    proposal_info = Field(ProposalGeneralInfo)

    def resolve_proposal_id(self, args, context, info):
        return "proposal: " + str(self.proposal_id)

    def resolve_proposal_info(self, args, contect, info):
        general_info = ProposalGeneralInfoModel.query.get(self.ProposalCode_Id)
        return general_info


    @staticmethod
    def get_proposal_ids(**args):
        sql = " SELECT MAX(p.Proposal_Id) as Ids, p.ProposalCode_Id as PCode_Ids " \
              "  FROM Proposal AS p " \
              "    JOIN ProposalCode AS pc ON (p.ProposalCode_Id=pc.ProposalCode_Id) " \
              "    JOIN MultiPartner AS mp ON (p.ProposalCode_Id=mp.ProposalCode_Id) " \
              "    JOIN Partner AS pa ON (mp.Partner_Id=pa.Partner_Id) " \
              "    JOIN ProposalGeneralInfo AS pgi ON (pgi.ProposalCode_Id=p.ProposalCode_Id) " \
              "    JOIN ProposalInvestigator AS pi ON (pi.ProposalCode_Id=p.ProposalCode_Id) " \
              "  WHERE Phase=1 AND ProposalStatus_Id not in (4, 9, 6, 8, 5, 3, 100) "
        if 'semester' in args:
            semester = TypeSemester.get_semester(semester_code=args['semester'])
            sql = sql + " AND mp.Semester_Id = {semester_id} ".format(semester_id=semester.id)

        if 'partner_code' in args and args['partner_code'] is not None:
            sql = sql + "AND pa.Partner_Code = '{parner_code}' ".format(parner_code=args['partner_code'])

        if 'proposal_code' in args and args['proposal_code'] is not None:
            sql = sql + "AND pc.Proposal_Code = '{proposal_code}' ".format(proposal_code=args['proposal_code'])

        if g.user.user_value == 0:
            return {'ProposalIds': [], 'ProposalCodeIds': []}

        elif g.user.user_value == 1:
            sql = sql + " AND pi.Investigator_Id = {inverstitagor_id}".format(inverstitagor_id=g.user.user_id)

        sql = sql + " GROUP BY pc.ProposalCode_Id "
        results = pd.read_sql(sql, conn)
        ids = [int(x) for x in list(results['Ids'].values)]
        pcode_ids = [int(x) for x in list(results['PCode_Ids'].values)]
        return {'ProposalIds': ids, 'ProposalCodeIds': pcode_ids}


class ProposalCode(SQLAlchemyObjectType):
    class Meta:
        interfaces = (relay.Node, )
        model = ProposalCodeModel


class ProposalContact(SQLAlchemyObjectType):
    class Meta:
        interfaces = (relay.Node, )
        model = ProposalContactModel


class Investigator(SQLAlchemyObjectType):
    class Meta:
        interfaces = (relay.Node, )
        model = InvestigatorModel


class Semester(SQLAlchemyObjectType):
    class Meta:
        interfaces = (relay.Node, )
        model = SemesterModel


class SemesterPhase(SQLAlchemyObjectType):
    class Meta:
        interfaces = (relay.Node, )
        model = SemesterPhaseModel


class ProposalType(SQLAlchemyObjectType):
    class Meta:
        interfaces = (relay.Node, )
        model = ProposalTypeModel



class ProposalStatus(SQLAlchemyObjectType):
    class Meta:
        interfaces = (relay.Node, )
        model = ProposalStatusModel


class P1ObservingConditions(SQLAlchemyObjectType):
    class Meta:
        interfaces = (relay.Node, )
        model = P1ObservingConditionsModel


class Transparency(SQLAlchemyObjectType):
    class Meta:
        interfaces = (relay.Node, )
        model = TransparencyModel



proposals_list = [
    Investigator,
    MultiPartner,
    P1ObservingConditions,
    Partner,
    Proposal,
    ProposalCode,
    ProposalContact,
    ProposalGeneralInfo,
    ProposalStatus,
    Semester,
    SemesterPhase,
    Transparency,
    ProposalType
]
