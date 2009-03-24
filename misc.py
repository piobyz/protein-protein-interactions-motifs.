import logging
import logging.config

import random # random.choice in output_fasta_file()

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


def output_fasta_file(most_interacting_interfaces, true_negatives_set=False):
    """Creates FASTA file with true positives OR true negatives from most interacting pairs of 3DID domains."""
    # Create FASTA file with interacting domain pairs interfaces sequence
    if true_negatives_set:
        try:
            fasta_output = open('results/most_interacting_domain_pairs_interfaces-TN.fa', 'w')
        except IOError:
            log_load.exception("Unable to create a file: %s " % "results/most_interacting_domain_pairs_interfaces-TN.fa")
            
        interactors = []
        
        # Put each interactor from interacting pair of domains in one list
        for entry in most_interacting_interfaces:
            pdb_one = entry[0].strip()
            chain_one = entry[1].strip()
            seq_one = entry[5].strip()
            
            interactors.append((pdb_one, chain_one, seq_one))

            pdb_two = entry[2].strip()
            chain_two = entry[3].strip()
            seq_two = entry[6].strip()
            
            interactors.append((pdb_two, chain_two, seq_two))
        
        # Randomly choose two interactors and store them as (falsely) interacting pair
        for i in range(len(interactors)/2):
            interactor_one = random.choice(interactors)
            interactor_two = random.choice(interactors)
            
            pdb_one = interactor_one[0].strip()
            chain_one = interactor_one[1].strip()
            seq_one = interactor_one[2].strip()

            pdb_two = interactor_two[0].strip()
            chain_two = interactor_two[1].strip()
            seq_two = interactor_two[2].strip()
        
            to_write = '> %s%s - %s%s\n%s%s\n' % (pdb_one, chain_one, pdb_two, chain_two, seq_one, seq_two)
            fasta_output.write(to_write)

    else:
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
