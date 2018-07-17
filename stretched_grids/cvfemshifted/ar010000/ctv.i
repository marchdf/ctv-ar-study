# -*- mode: yaml -*-
Simulations:
  - name: sim1
    time_integrator: ti_1
    optimizer: opt1
    error_estimator: errest_1

linear_solvers:

  - name: hypre_mom
    type: hypre
    method: hypre_gmres
    preconditioner: boomerAMG
    tolerance: 1e-5
    max_iterations: 100
    kspace: 10
    output_level: 0
    write_matrix_files: off
    bamg_output_level: 0
    bamg_coarsen_type: 8
    bamg_interp_type: 6
    bamg_cycle_type:  1
    bamg_relax_type: 3
    bamg_relax_order: 1
    bamg_num_sweeps: 2
    bamg_keep_transpose: 1
    bamg_max_levels: 1
    bamg_trunc_factor: 0.1
    bamg_pmax_elmts: 2
    bamg_strong_threshold: 0.25
    absolute_tolerance: 1.0e-12

  - name: hypre_cont
    type: hypre
    method: hypre_gmres
    preconditioner: boomerAMG
    tolerance: 1e-5
    max_iterations: 100
    kspace: 10
    output_level: 0
    absolute_tolerance: 1.0e-12

realms:

  - name: realm_1
    mesh: ../../mesh/mesh_512x512_10000.exo
    use_edges: no
    automatic_decomposition_type: rib

    equation_systems:
      name: theEqSys
      max_iterations: 2
   
      solver_system_specification:
        pressure: hypre_cont
        velocity: hypre_mom

      systems:
        - LowMachEOM:
            name: myLowMach
            max_iterations: 1
            convergence_tolerance: 1e-8

    initial_conditions:

      - user_function: ic_1
        target_name: interior
        user_function_name:
         velocity: convecting_taylor_vortex
         pressure: convecting_taylor_vortex

    material_properties:
      target_name: interior

      specifications:
        - name: density
          type: constant
          value: 1.0

        - name: viscosity
          type: constant
          value: 0.001

    boundary_conditions:

    - periodic_boundary_condition: bc_left_right
      target_name: [north, south]
      periodic_user_data:
        search_tolerance: 1.e-5
        search_method: boost_rtree

    - periodic_boundary_condition: bc_left_right
      target_name: [west, east]
      periodic_user_data:
        search_tolerance: 1.e-5
        search_method: boost_rtree

    - symmetry_boundary_condition: bc1
      target_name: top
      symmetry_user_data:

    - symmetry_boundary_condition: bc2
      target_name: bottom
      symmetry_user_data:


    solution_options:
      name: myOptions
      turbulence_model: laminar
      use_consolidated_solver_algorithm: no

      options:
        - hybrid_factor:
            velocity: 0.0

        - limiter:
            pressure: no
            velocity: no

        - shifted_gradient_operator:
            velocity: yes
            pressure: yes

        - consistent_mass_matrix_png:
            pressure: no

    output:
      output_data_base_name: results/ctv.e
      output_frequency: 1000
      output_node_set: no 
      output_variables:
       - dual_nodal_volume
       - velocity
       - velocity_exact

    solution_norm:
      output_frequency: 1
      file_name: ctv.dat
      spacing: 12
      percision: 6
      target_name: block_1
      dof_user_function_pair:
       - [velocity, convecting_taylor_vortex]
       - [dpdx, convecting_taylor_vortex_dpdx]

Time_Integrators:
  - StandardTimeIntegrator:
      name: ti_1
      start_time: 0
      termination_step_count: 50000
      time_step: 0.0000001953125
      time_stepping_type: fixed 
      time_step_count: 0
      second_order_accuracy: yes

      realms:
        - realm_1
