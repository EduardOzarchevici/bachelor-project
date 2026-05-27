package org.fitblocker.service;

import org.fitblocker.model.AppUser;
import org.fitblocker.repository.AppUserRepository;
import org.fitblocker.security.UserPrincipal;
import org.springframework.security.core.userdetails.User;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;

import java.util.ArrayList;

@Service
public class CustomUserDetailsService implements UserDetailsService {

    private final AppUserRepository repository;

    public CustomUserDetailsService(AppUserRepository repository) {
        this.repository = repository;
    }

    @Override
    public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
        AppUser user = repository.findByUsername(username)
                .orElseThrow(() -> new UsernameNotFoundException("User not found"));
        return new User(user.getUsername(), user.getPassword(), new ArrayList<>());
    }

    public UserPrincipal loadUserById(Long id) {
        AppUser user = repository.findById(id)
                .orElseThrow(() -> new RuntimeException("User not found"));
        return new UserPrincipal(user);
    }
}