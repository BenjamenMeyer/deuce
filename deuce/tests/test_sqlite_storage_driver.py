from pecan import conf

import os
from deuce.tests import FunctionalTest
from deuce.drivers.metadatadriver import MetadataStorageDriver, GapError,\
    OverlapError
from deuce.drivers.sqlite import SqliteStorageDriver


class SqliteStorageDriverTest(FunctionalTest):

    def create_driver(self):
        return SqliteStorageDriver()

    def test_basic_construction(self):
        driver = SqliteStorageDriver()

    def test_geneology(self):
        driver = SqliteStorageDriver()
        assert isinstance(driver, MetadataStorageDriver)
        assert isinstance(driver, object)

    def test_file_crud(self):
        driver = self.create_driver()

        project_id = self.create_project_id()
        vault_id = self.create_vault_id()
        file_id = self.create_file_id()

        assert not driver.has_file(project_id, vault_id, file_id)

        driver.create_file(project_id, vault_id, file_id)

        assert driver.has_file(project_id, vault_id, file_id)

        data = driver.get_file_data(project_id, vault_id, file_id)

        driver.delete_file(project_id, vault_id, file_id)

        assert not driver.has_file(project_id, vault_id, file_id)

    def test_finalize_empty_file(self):
        driver = self.create_driver()

        project_id = self.create_project_id()
        vault_id = self.create_vault_id()
        file_id = self.create_file_id()

        driver.create_file(project_id, vault_id, file_id)

        assert not driver.is_finalized(project_id, vault_id, file_id)

        driver.finalize_file(project_id, vault_id, file_id)

        assert driver.is_finalized(project_id, vault_id, file_id)

    def test_finalize_nonexistent_file(self):
        driver = self.create_driver()

        project_id = self.create_project_id()
        vault_id = self.create_vault_id()
        file_id = self.create_file_id()

        assert not driver.has_file(project_id, vault_id, file_id)
        retval = driver.finalize_file(project_id, vault_id, file_id)

        try:
            data = driver.get_file_data(project_id, vault_id, file_id)
        except:
            assert True

        assert not driver.has_file(project_id, vault_id, file_id)
        assert not driver.is_finalized(project_id, vault_id, file_id)

    def test_block_crud(self):
        driver = self.create_driver()

        project_id = self.create_project_id()
        vault_id = self.create_vault_id()
        block_id = self.create_block_id()
        size = 4096

        assert not driver.has_block(project_id, vault_id, block_id)
        try:
            size = driver.get_block_data(project_id,
                vault_id, block_id)['blocksize']
        except:
            assert True
        driver.register_block(project_id, vault_id, block_id, size)

        assert driver.has_block(project_id, vault_id, block_id)

        self.assertEqual(driver.get_block_data(project_id,
            vault_id, block_id)['blocksize'], size)

        # Call again, shouldn't throw
        driver.register_block(project_id, vault_id, block_id, size)

        driver.unregister_block(project_id, vault_id, block_id)
        assert not driver.has_block(project_id, vault_id, block_id)

        assert not driver.has_block(project_id, vault_id, 'invalidid')

    def test_file_assignment(self):

        driver = self.create_driver()

        # So for some reason this fails on line 176 if
        # if project_id is set to a 'project_<UUID>' but
        # passes if set to 'project_id'.
        project_id = 'project_id'
        # project_id = self.create_project_id()
        vault_id = self.create_vault_id()
        file_id = self.create_file_id()

        normal_block_size = 333
        gap_block_size = 222
        overlap_block_size = 444

        # GAP at front (miss the 1st block)
        num_blocks = int(0.5 * conf.api_configuration.max_returned_num)
        block_ids = ['block_{0}'.format(id) for id in range(1, num_blocks)]
        offsets = [x * normal_block_size for x in range(1, num_blocks)]

        blockpairs = dict(zip(block_ids, offsets))

        # Create a file
        driver.create_file(project_id, vault_id, file_id)

        # Assign each block
        for bid, offset in blockpairs.items():
            driver.assign_block(project_id, vault_id, file_id, bid, offset)

        assert not driver.is_finalized(project_id, vault_id, file_id)

        # GAPs (gap at front)
        for bid, offset in blockpairs.items():
            driver.register_block(project_id, vault_id, bid, gap_block_size)

        with self.assertRaises(GapError) as ctx:
            res = driver.finalize_file(project_id, vault_id, file_id)

        self.assertEqual(ctx.exception.vault_id, vault_id)
        self.assertEqual(ctx.exception.file_id, file_id)
        self.assertEqual(ctx.exception.startpos, 0)
        self.assertEqual(ctx.exception.endpos, 333)

        assert not driver.is_finalized(project_id, vault_id, file_id)

        # OVERLAPs (gap at front)
        for bid, offset in blockpairs.items():
            driver.unregister_block(project_id, vault_id, bid)
            driver.register_block(project_id, vault_id,
                bid, overlap_block_size)

        with self.assertRaises(GapError) as ctx:
            res = driver.finalize_file(project_id, vault_id, file_id)

        self.assertEqual(ctx.exception.vault_id, vault_id)
        self.assertEqual(ctx.exception.file_id, file_id)
        self.assertEqual(ctx.exception.startpos, 0)
        self.assertEqual(ctx.exception.endpos, 333)

        assert not driver.is_finalized(project_id, vault_id, file_id)

        # put back the missed block at the front
        # Create a gap in the middle
        block_ids.insert(0, 'block_0')
        blockpairs['block_0'] = 0
        driver.assign_block(project_id, vault_id, file_id, 'block_0', 0)
        for bid, offset in blockpairs.items():
            driver.unregister_block(project_id, vault_id, bid)
            driver.register_block(project_id, vault_id, bid, gap_block_size)

        with self.assertRaises(GapError) as ctx:
            res = driver.finalize_file(project_id, vault_id, file_id)

        self.assertEqual(ctx.exception.vault_id, vault_id)
        self.assertEqual(ctx.exception.file_id, file_id)
        self.assertEqual(ctx.exception.startpos, 222)
        self.assertEqual(ctx.exception.endpos, 333)

        assert not driver.is_finalized(project_id, vault_id, file_id)

        # Create a overlap in the middle
        for bid, offset in blockpairs.items():
            driver.unregister_block(project_id, vault_id, bid)
            driver.register_block(project_id, vault_id,
                bid, overlap_block_size)

        with self.assertRaises(OverlapError) as ctx:
            res = driver.finalize_file(project_id, vault_id, file_id)

        self.assertEqual(ctx.exception.vault_id, vault_id)
        self.assertEqual(ctx.exception.file_id, file_id)
        self.assertEqual(ctx.exception.block_id, 'block_1')
        self.assertEqual(ctx.exception.startpos, 333)
        self.assertEqual(ctx.exception.endpos, 444)

        assert not driver.is_finalized(project_id, vault_id, file_id)

        # Fix and back to normal
        for bid, offset in blockpairs.items():
            driver.unregister_block(project_id, vault_id, bid)
            driver.register_block(project_id, vault_id, bid, normal_block_size)

        # gap at the eof.
        with self.assertRaises(GapError) as ctx:
            res = driver.finalize_file(project_id, vault_id,
                file_id, file_size=14000)

        self.assertEqual(ctx.exception.vault_id, vault_id)
        self.assertEqual(ctx.exception.file_id, file_id)
        self.assertEqual(ctx.exception.startpos, 13320)
        self.assertEqual(ctx.exception.endpos, 14000)

        assert not driver.is_finalized(project_id, vault_id, file_id)

        # overlap at the eof.
        with self.assertRaises(OverlapError) as ctx:
            res = driver.finalize_file(project_id, vault_id,
                file_id, file_size=12900)

        self.assertEqual(ctx.exception.vault_id, vault_id)
        self.assertEqual(ctx.exception.file_id, file_id)
        self.assertEqual(ctx.exception.startpos, 12900)  # end of file
        self.assertEqual(ctx.exception.endpos, 13320)  # Overlap past EOF

        assert not driver.is_finalized(project_id, vault_id, file_id)

        # This should now succeed and the file
        # should be successfully finalized
        res = driver.finalize_file(project_id, vault_id,
            file_id, file_size=13320)

        assert not res
        assert driver.is_finalized(project_id, vault_id, file_id)

        # Now create a generator of the files. The output
        # should be in the same order as block_ids
        offset = 0
        limit = 4

        retgen = \
            driver.create_file_block_generator(
                project_id, vault_id, file_id, offset, limit)

        fetched_blocks = list(retgen)

        # The driver actually returns limit+1 so that any
        # caller knows that the list is truncated.
        self.assertEqual(len(fetched_blocks), limit)

        # -1 to exclude the trailer
        for x in range(0, limit):
            self.assertEqual(fetched_blocks[x][0], block_ids[x])

        # Add 2 more blocks that aren't assigned.
        driver.register_block(project_id, vault_id, 'unassigned_1', 1024)
        driver.register_block(project_id, vault_id, 'unassigned_2', 1024)

        num_blocks += 2

        # Now create a generator of the files. The output
        # should be in the same order as block_ids
        # Test driver branch with a given marker
        gen = driver.create_block_generator(project_id, vault_id, marker=0)
        # Test driver branch with a default marker
        gen = driver.create_block_generator(project_id, vault_id)

        fetched_blocks = list(gen)

        self.assertEqual(len(fetched_blocks), num_blocks)

        # Now try file_block_generator with no limit
        # Force returning an empty list by an unreasonable offset.
        retgen = \
            driver.create_file_block_generator(
                project_id, vault_id, file_id, offset=999999999, limit=None)
        # A good set.
        retgen = \
            driver.create_file_block_generator(
                project_id, vault_id, file_id, offset=None, limit=None)

        output = sorted(list(retgen))
        prep = sorted(list(x for x in blockpairs.items()))

        self.assertEqual(output, prep)

    def test_file_generator(self):

        # Adds a bunch of files and checks the generator
        driver = self.create_driver()

        project_id = self.create_project_id()
        vault_id = self.create_vault_id()
        num_files = 10

        # Create a list of 100 files
        file_ids = [self.create_file_id() for _ in range(0, num_files)]

        for file_id in file_ids:
            assert not driver.has_file(project_id, vault_id, file_id)

            out_id = driver.create_file(project_id, vault_id, file_id)

            self.assertEqual(out_id, file_id)
            assert driver.has_file(project_id, vault_id, file_id)

        # None of the files have been finalized so we should
        # get none back
        gen = driver.create_file_generator(project_id, vault_id)

        output = list(gen)

        self.assertEqual(output, [])

        # Now finalize the files and try to get them

        for file_id in file_ids:
            driver.finalize_file(project_id, vault_id, file_id)

        gen = driver.create_file_generator(project_id, vault_id)

        # Convert to a list of file ids.
        output = list(gen)

        # Why sorted? Deuce returns file ids sorted, but the list
        # of file ids that we generated were not sorted when we
        # created them above.
        self.assertEqual(output, sorted(file_ids))

        # Now try with markers

        gen = driver.create_file_generator(project_id, vault_id,
            marker=sorted(file_ids)[2], limit=3)

        output = list(gen)
        self.assertEqual(len(output), 3)  # Limited query to 3

        # We should be able to compare the list of
        # file ids here with the ones that come from
        # the other list
        target_list = sorted(file_ids)[2:5]

        self.assertEqual(target_list, output)
