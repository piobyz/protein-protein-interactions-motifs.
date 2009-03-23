import logging
import logging.config

# Logging configuration
logging.config.fileConfig("log/logging.conf")
log_load = logging.getLogger('load')
log_results = logging.getLogger('results')


def compare_interactions(dip_interactions_source=None, three_did_interactions_source=None, jena_interactions_source=None, \
                            jena=False):
    """Take interactions from one set (DIP, 3DID or JENA) and find overlapping interactions in the other one."""
    dip_interactions = {}
    three_did_interactions = {}
    jena_interactions = {}

    # NOTE: JENA has only PDB ids - without chains
    # Final results will be written here in fasta format, 1st line: interactor's PDB1chain1 - PDB2chain2
    try:
        results_handler = open('results/overlapping-DIP-3DID.fa', 'w')
    except IOError:
        log_load.exception('Problems with creating file: %s' % results_handler)

    if dip_interactions_source:
        number_of_dip_interactions = 0
        if jena:
            for entry in dip_interactions_source:
                # Take only PDB ids, without chains, see NOTE above
                dip_interactions[entry[0]] = ''
                dip_interactions[entry[2]] = ''
                number_of_dip_interactions += 2
            else:
                for entry in dip_interactions_source:
                    dip_interactions[entry] = ''
                    number_of_dip_interactions += 1
        log_results.info('Number of DIP interactions: %s' % number_of_dip_interactions)

    if three_did_interactions_source:
        number_of_3did_interactions = 0
        if jena:
            for entry in three_did_interactions_source:
                # Take only PDB ids, without chains, see NOTE above
                three_did_interactions[entry[0]]=''
                three_did_interactions[entry[2]]=''
                number_of_3did_interactions += 2
        else:
            for entry in three_did_interactions:
                three_did_interactions[entry] = ''
                number_of_dip_interactions += 1
        log_results.info('Number of 3DID interactions: %s' % number_of_3did_interactions)

    if jena_interactions_source:
        number_of_jena_interactions = 0
        for entry in jena_interactions_source:
            jena_interactions[entry] = ''
            number_of_jena_interactions += 1
    log_results.info('Number of JENA interactions: %s' % number_of_jena_interactions)

    # Find interactions overlapping in two sets
    if jena:
        # Find overlaps in DIP and JENA
        overlapping_dip_jena = 0
        for k in jena_interactions.keys():
            if k in dip_interactions.keys():
                to_write = '> %s\n' % k
                log_results.info('Overlapping DIP-JENA: %s' % to_write)
                overlapping_dip_jena += 1
        log_results.info('Number of overlapping DIP-JENA: %s' % overlapping_dip_jena)

        # Find overlaps in 3DID and JENA
        overlapping_3did_jena = 0
        for k in jena_interactions.keys():
            if k in three_did_interactions:
                to_write = '> %s\n' % k
                log_results.info('Overlapping 3DID-JENA: %s' % to_write)
                overlapping_3did_jena += 1
        log_results.info('Number of overlapping 3DID-JENA: %s' % overlapping_3did_jena)

    else:
        # Find overlaps in DIP and 3DID
        overlapping_dip_3did = 0
        for k in dip_interactions.keys():
            if k in three_did_interactions:
                to_write = '> %s\n%s\n' % (k, three_did_interactions[k])
                results_handler.write(to_write)
                overlapping_dip_3did += 1
        log_results.info('Number of overlapping DIP-3DID: %s' % overlapping_dip_3did)

    results_handler.close()
    log_results.info('Results written to: %s' % results_handler.name)


def output_fasta_file(most_interacting_interfaces):
    """docstring for output_fasta_file"""
    # Create FASTA file with interacting domain pairs interfaces sequence
    try:
        fasta_output = open('results/most_interacting_domain_pairs_interfaces.fa', 'w')
    except IOError:
        log_load.exception("Unable to create a file: %s " % "results/most_interacting_domain_pairs_interfaces.fa")

    for entry in most_interacting_interfaces:
        pdb_one = entry[0].strip()
        chain_one = entry[1].strip()
        pdb_two = entry[2].strip()
        chain_two = entry[3].strip()
        interface = entry[4].strip()

        to_write = '> %s%s - %s%s\n%s\n' % (pdb_one, chain_one, pdb_two, chain_two, interface)
        fasta_output.write(to_write)

    fasta_output.close()


def calculate_sequence_identity():
    """docstring for calculate_sequence_identity"""
    # Calculate identity % between 2 sequences

    from Bio import pairwise2

    alignments = pairwise2.align.globalxx("ACCGT", "ACG")
    # x No parameters.  Identical characters have score of 1, otherwise 0.
    # x No gap penalties.
    # http://www.biopython.org/DIST/docs/api/Bio.pairwise2-module.html

    identity = (alignments[0][2] / (alignments[0][4]+1))*100
    
    return identity
