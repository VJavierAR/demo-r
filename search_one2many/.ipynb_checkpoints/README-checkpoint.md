RP Quick Search in one2many
----------------------------

Overview
--------
This module allows to quick search in One2many field.

Configuration
--------------
Required configuration:

1. For existing where widget='section_and_note_one2many' is given replace by section_and_note_one2many_custom by using xpath.
For example:- 
```xml
<xpath expr="//field[@name='order_line']" position="attributes">
    <attribute name="widget">section_and_note_one2many_custom</attribute>
</xpath>
```

2. For new (i.e. where 'section_and_note_one2many' is not given but you want to give) then you can directly put widget='section_and_note_one2many_custom'.



Usage
-----
By Default in one2mnay fiels if one2many lines are more then it is very difficult to search next pager items. So, To overcome from this allow to search in One2many field.

Connect with experts
--------------------

If you have any question/queries on this module, You can drop an email directly to Us.

Contacts
--------
info - rpodoodeveloper@gmail.com

