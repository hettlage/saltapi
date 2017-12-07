import pandas as pd
from data import sdb_connect


def get_partners(semester, partner):
    from schema.partner import PartnerAllocations, AllocatedTime

    sql = ' select * from  PeriodTimeDist ' \
          '    join Partner using(Partner_Id)  ' \
          '    join Semester using(Semester_Id)  ' \
          ' where concat(Year,"-", Semester) = "{semester}" ' \
          ' '.format(semester=semester)
    if partner is not None:
        sql = sql + ' and Partner_Code = "{partner_code}" '.format(partner_code=partner)

    conn = sdb_connect()
    results = pd.read_sql(sql, conn)
    conn.close()

    partners = [PartnerAllocations(
        id="Partner: " + str(row["Partner_Id"]),
        name=row["Partner_Name"],
        code=row["Partner_Code"],
        allocated_time=AllocatedTime(
            for_semester=str(row['Year']) + "-" + str(row['Semester']),

            Allocated_p0_p1=row['Alloc0and1'],
            Allocated_p2=row['Alloc2'],
            Allocated_p3=row['Alloc3'],

            used_p0_p1=row['Used0and1'],
            used_p2=row['Used2'],
            used_p3=row['Used3']
        )) for index, row in results.iterrows()]

    return partners


def get_partners_for_role(ids=None):
    par = 'select Partner_Code from Partner '
    if ids is not None:
        if len(ids) == 1:
            par = par + ' where Partner_Id = {id}'.format(id=ids[0])
        else:
            par = par + ' where Partner_Id in {ids}'.format(ids=tuple(ids))

    conn = sdb_connect()
    results = pd.read_sql(par, conn)
    conn.close()

    return [row["Partner_Code"] for i, row in results.iterrows()]
