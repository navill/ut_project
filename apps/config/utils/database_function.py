from django.db.models import Func


class CalculateAge(Func):
    """
       CREATE DEFINER=`root`@`%` FUNCTION `calculate_age`(birth_date DATE) RETURNS int(11)
       BEGIN
       declare result_age integer default 0;
       set result_age = truncate((to_days(now())-(to_days(birth_date)))/365, 0);
       RETURN result_age;
       END
    """
    function = 'calculate_age'
