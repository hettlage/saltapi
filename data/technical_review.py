from flask import g
from util.action import Action
from data.common import sdb_connect


def update_technical_reports(semester, reports):
    """
    Update the database with a list of technical reports.

    Parameters
    ----------
    semester : str
        The semester, such as `2017-2` or `2018-1`, for which the technical reports are updated.
    reports : iterable
        The list of technical reports. Each report must be a dictionary with a proposal code and a report,
        such as `{'proposal_code': '2017-2-SCI-042', 'report': 'this is proposal is feasible'}`.
    """

    connection = sdb_connect()
    try:
        with connection.cursor() as cursor:
            for report in reports:
                update_technical_report(proposal_code=report['proposalCode'],
                                        semester=semester,
                                        report=report['report'],
                                        cursor=cursor)
            connection.commit()
    finally:
        connection.close()


def update_technical_report(proposal_code, semester, report, cursor):
    """
    Update a proposal's technical report.

    If no entry exists for the proposal and semester, a new entry is created with the logged in
    user as reporting astronomer. If an entry exists, its TechReport column value is updated,
    but the reporting user is left unchanged.

    This function executes the insert statement on the given cursor, but it does not explicitly
    commit. You might have to commit the transaction in a function using this one.

    Parameters
    ----------
    proposal_code : str
        Proposal code of the proposal.
    semester : str
        Semester, such as '2017-2; or '2018-1'.
    report : str
        Technical report.
    cursor: database cursor
        Cursor on which the database command is executed.

    Returns
    -------
    void
    """

    if not g.user.may_perform(Action.UPDATE_TECHNICAL_REPORT, proposal_code=proposal_code):
        raise Exception('You are not allowed to update the technical report of proposal {proposal_code}'
                        .format(proposal_code=proposal_code))

    year, sem = semester.split('-')
    sql = '''INSERT INTO ProposalTechReport (ProposalCode_Id, Semester_Id, Astronomer_Id, TechReport)
                    SELECT pc.ProposalCode_Id, s.Semester_Id, u.Investigator_Id, %s
                           FROM ProposalCode AS pc, Semester AS s, PiptUser AS u
                           WHERE pc.Proposal_Code=%s AND (s.Year=%s AND s.Semester=%s) AND  u.Username=%s
                    ON DUPLICATE KEY UPDATE Astronomer_Id=IF(TRIM(TechReport)!='', Astronomer_Id, u.Investigator_Id), TechReport=%s'''
    cursor.execute(sql, (report, proposal_code, year, sem, g.user.username, report))


def update_liaison_astronomers(assignments):
    """
    Update the database with a list of time allocations.

    Parameters
    ----------
    assignments : iterable
        The list of liaison astronomer assignments. Each assignment must be dictionary with a proposal code and
        a username (of the SALT Astronomer to be assigned to that proposal).
    """

    connection = sdb_connect()
    try:
        with connection.cursor() as cursor:
            for assignment in assignments:
                update_liaison_astronomer(proposal_code=assignment['proposalCode'],
                                          liaison_astronomer=assignment['liaisonAstronomer'],
                                          cursor=cursor)
            connection.commit()
    finally:
        connection.close()


def update_liaison_astronomer(proposal_code, liaison_astronomer, cursor):
    """
    Update a proposal's liaison astronomer.

    Parameters
    ----------
    proposal_code : str
        Proposal code of the proposal.
    liaison_astronomer : str
        Username of the liaison astronomer.
    cursor : database cursor
        Cursor on which the database command is executed.

    Returns
    -------
    void
    """

    if not g.user.may_perform(Action.UPDATE_LIAISON_ASTRONOMER,
                              proposal_code=proposal_code,
                              liaison_astronomer=liaison_astronomer):
        raise Exception('You are not allowed to update the liaison astronomer of proposal {proposal_code}'
                        .format(proposal_code=proposal_code))

    if liaison_astronomer is not None:
        sql = '''UPDATE ProposalContact SET Astronomer_Id=
                        (SELECT PiptUser.Investigator_Id
                                FROM PiptUser
                         WHERE PiptUser.Username=%s)
                 WHERE ProposalContact.ProposalCode_Id=
                       (SELECT ProposalCode.ProposalCode_Id
                        FROM ProposalCode
                        WHERE ProposalCode.Proposal_Code=%s)'''
        params = (liaison_astronomer, proposal_code)
    else:
        sql = '''UPDATE ProposalContact SET Astronomer_Id=NULL
                 WHERE ProposalContact.ProposalCode_Id=
                       (SELECT ProposalCode.ProposalCode_Id
                        FROM ProposalCode
                        WHERE ProposalCode.Proposal_Code=%s)'''
        params = (proposal_code,)
    cursor.execute(sql, params)


def update_reviewers(semester, assignments):
    """
    Update the database with a list of reviwers.

    Parameters
    ----------
    semester : str
        Semester, such as "2018-1".
    assignments : iterable
        The list of reviwewer assignments. Each assignment must be dictionary with a proposal code and
        a username (of the SALT Astronomer to be assigned as reviewer to that proposal).
    """

    connection = sdb_connect()
    try:
        with connection.cursor() as cursor:
            for assignment in assignments:
                update_reviewer(proposal_code=assignment['proposalCode'],
                                semester=semester,
                                reviewer=assignment['reviewer'],
                                cursor=cursor)
            connection.commit()
    finally:
        connection.close()


def update_reviewer(proposal_code, semester, reviewer, cursor):
    """
    Update a proposal's reviewer.

    Parameters
    ----------
    proposal_code : str
        Proposal code of the proposal.
    semester : str
        Semester, such as "2018-1".
    reviewer : str
        Username of the reviewer.
    cursor : database cursor
        Cursor on which the database command is executed.

    Returns
    -------
    void
    """

    if not g.user.may_perform(Action.UPDATE_REVIEWER,
                              proposal_code=proposal_code,
                              reviewer=reviewer):
        raise Exception('You are not allowed to update the reviewer of proposal {proposal_code}'
                        .format(proposal_code=proposal_code))

    year, sem = semester.split('-')
    if reviewer is not None:
        sql = '''UPDATE ProposalTechReport SET Astronomer_Id=
                        (SELECT PiptUser.Investigator_Id
                                FROM PiptUser
                         WHERE PiptUser.Username=%s)
                 WHERE ProposalTechReport.ProposalCode_Id=
                       (SELECT ProposalCode.ProposalCode_Id
                        FROM ProposalCode
                        WHERE ProposalCode.Proposal_Code=%s)
                       AND ProposalTechReport.Semester_Id=
                           (SELECT Semester.Semester_Id
                            FROM Semester
                            WHERE Semester.Year=%s AND Semester.Semester=%s)'''
        params = (reviewer, proposal_code, year, sem)
    else:
        sql = '''UPDATE ProposalTechReport SET Astronomer_Id=NULL
                 WHERE ProposalTechReport.ProposalCode_Id=
                       (SELECT ProposalCode.ProposalCode_Id
                        FROM ProposalCode
                        WHERE ProposalCode.Proposal_Code=%s)
                       AND ProposalTechReport.Semester_Id=
                           (SELECT Semester.Semester_Id
                            FROM Semester
                            WHERE Semester.Year=%s AND Semester.Semester=%s)'''
        params = (proposal_code, year, sem)
    cursor.execute(sql, params)
