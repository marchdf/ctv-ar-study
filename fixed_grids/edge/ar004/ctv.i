# -*- mode: yaml -*-
Simulations:
  - name: sim1
    time_integrator: ti_1
    optimizer: opt1
    error_estimator: errest_1

linear_solvers:

  - name: solve_scalar
    type: tpetra
    method: gmres
    preconditioner: ilut
    tolerance: 1e-5
    max_iterations: 300
    kspace: 100
    output_level: 0


  - name: solve_cont
    type: tpetra
    method: gmres
    preconditioner: muelu
    tolerance: 1e-5
    max_iterations: 75
    kspace: 75
    output_level: 0
    muelu_xml_file_name: ../../muelu.xml
    recompute_preconditioner: no

realms:

  - name: realm_1
    mesh: ../../mesh/mesh_256x1024.exo
    use_edges: yes
    automatic_decomposition_type: rib

    equation_systems:
      name: theEqSys
      max_iterations: 5
   
      solver_system_specification:
        pressure: solve_cont
        velocity: solve_scalar
        dpdx: solve_scalar

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
      termination_time: 1.0
      time_step: 0.00048828125
      time_stepping_type: fixed 
      time_step_count: 0
      second_order_accuracy: yes

      realms:
        - realm_1
