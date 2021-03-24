from django.db.models import Func


class CalculateAge(Func):
    """
    MySQL - FUNCTION
       CREATE DEFINER=`root`@`%` FUNCTION `calculate_age`(birth_date DATE) RETURNS int(11)
       BEGIN
         declare result_age integer default 0;
         set result_age = floor((cast(replace(current_date, '-', '') as unsigned) - cast(brith_date as unsigned)) / 10000);
       RETURN result_age;
       END
    """
    function = 'calculate_age'
