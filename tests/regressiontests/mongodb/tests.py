from django.db.models import Count
from django.test import TestCase

from models import Artist, Group


class MongoTestCase(TestCase):
    def test_create(self):
        b = Artist.objects.create(name="Bruce Springsteen", good=True)
        self.assertTrue(b.pk is not None)
        self.assertEqual(b.name, "Bruce Springsteen")
        self.assertTrue(b.good)
        b2 = Artist.objects.get(pk=b.pk)
        self.assertEqual(b.pk, b2.pk)
        self.assertEqual(b.name, b2.name)
        self.assertEqual(b.good, b2.good)
    
    def test_update(self):
        l = Artist.objects.create(name="Lady Gaga", good=True)
        self.assertTrue(l.pk is not None)
        pk = l.pk
        # Whoops, we screwed up.
        l.good = False
        l.save()
        self.assertEqual(l.pk, pk)
        
        l = Artist.objects.get(pk=pk)
        self.assertTrue(not l.good)
    
    def test_count(self):
        Artist.objects.create(name="Billy Joel", good=True)
        Artist.objects.create(name="John Mellencamp", good=True)
        Artist.objects.create(name="Warren Zevon", good=True)
        Artist.objects.create(name="Matisyahu", good=True)
        Artist.objects.create(name="Gary US Bonds", good=True)
        
        self.assertEqual(Artist.objects.count(), 5)
        self.assertEqual(Artist.objects.filter(good=True).count(), 5)
        
        Artist.objects.create(name="Bon Iver", good=False)
        
        self.assertEqual(Artist.objects.count(), 6)
        self.assertEqual(Artist.objects.filter(good=True).count(), 5)
        self.assertEqual(Artist.objects.filter(good=False).count(), 1)
        
        self.assertEqual(Artist.objects.aggregate(c=Count("pk")), {"c": 6})
    
    def test_foreignkey(self):
        e = Group.objects.create(name="The E Street Band")
        b = Artist.objects.create(name="Clarence Clemons", good=True,
            current_group=e)
        
        self.assertEqual(b.current_group, e)
        self.assertEqual(b.current_group_id, e.pk)
        
        b = Artist.objects.get(name="Clarence Clemons")
        self.assertEqual(b.current_group_id, e.pk)
        self.assertFalse(hasattr(b, "_current_group_cache"))
        self.assertEqual(b.current_group, e)
    
    def test_lookup(self):
        q = Group.objects.create(name="Queen", year_formed=1971)
        e = Group.objects.create(name="The E Street Band", year_formed=1972)
        
        qs = Group.objects.exclude(year_formed=1972)
        v = qs.query.get_compiler(qs.db).get_filters(qs.query.where, correct=True)
        self.assertEqual(v, {
            "$or": [
                {"year_formed": {"$ne": 1972}},
                {"year_formed": None},
            ]
        })
        # A bug in MongoDB prevents this query from actually working, but test
        # that we're at least generating the right query.
        return
        
        self.assertQuerysetEqual(
            qs, [
                "Queen",
            ],
            lambda g: g.name,
        )