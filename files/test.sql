CREATE PROCEDURE `exportData` ()
BEGIN
select *,0 as `type`
from 
(
Select orderid, sum(`Braadworst`) as Braadworst,
	sum(`Halal Bicky Burger`) as `Halal Bicky Burger`,
    sum(`Drankbon`) as `Drankbon`
from (

select x.orderid,
	sum( case when x.productname = 'Braadworst' then x.number else 0 end) as Braadworst,
    sum( case when x.productname = 'Halal Bicky Burger' then x.number else 0 end) as `Halal Bicky Burger`,
    sum( case when x.productname = 'Drankbon' then x.number else 0 end) as Drankbon
    
FROM (
    SELECT `order`.`id` as `orderid`, `order`.`name` as `name`, `order`.`email` as `email`, 
		orderlines.number, product.name as `productname`, product.price, product.price * orderlines.number as `total_price`
    FROM `order` 
	LEFT JOIN `orderlines` ON `orderlines`.`order_id` = `order`.`id`
    INNER join product on product.id = orderlines.product_id
  ) as x
  group by x.productname, x.orderid
  ) as y
  inner join `order` o on o.id = y.orderid
  group by orderid
  ) as z
  inner join `order` o on o.id = z.orderid;
END
