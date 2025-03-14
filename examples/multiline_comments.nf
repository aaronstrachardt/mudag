#!/usr/bin/env nextflow

// This is a single line comment in Nextflow

/* 
 * This is a multiline comment in Nextflow.
 * All of these lines should be counted as comments.
 * This is the preferred style for documenting processes.
 */

// Define input parameters
params.input = 'data/*.txt'
params.output = 'results/'

/* 
 * Another multiline comment
 * with multiple lines
 */

process PROCESS_DATA {
    input:
    path datafile

    output:
    path 'processed.txt'

    script:
    """
    # This line won't be counted as a comment because it's inside a script block
    echo "Processing ${datafile}" > processed.txt
    cat ${datafile} >> processed.txt
    """
}

workflow {
    Channel.fromPath(params.input)
    | PROCESS_DATA
    | collectFile(name: 'all_results.txt', storeDir: params.output)
} 